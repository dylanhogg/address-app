# https://aws.amazon.com/blogs/compute/deploying-machine-learning-models-with-serverless-templates/
PROFILE=prd-non-tf-905234897161
PROJECT_NAME=test-sam-prj-addressnet
AWS_ACCOUNT=905234897161
AWS_REGION=us-east-1

test-build:
	cd app; docker build -t ${PROJECT_NAME}-manual-build .

bash-test-build:
	docker run -it --entrypoint=/bin/bash ${PROJECT_NAME}-manual-build

init:
	sam init --runtime python3.7 --name ${PROJECT_NAME}

sam-validate:
	sam validate --profile ${PROFILE}

build:
	sam build

local:
	# sam local invoke InferenceFunction
	sam local invoke InferenceFunction --event events/event.json

api:
	sam local start-api

sam-gen-event:
	# To test
	# https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/serverless-getting-started-hello-world.html
	sam local generate-event apigateway aws-proxy --body "" --path "hello" --method GET > api-event.json
	diff api-event.json events/event.json

login-ecr:
	aws --profile ${PROFILE} --region ${AWS_REGION} ecr get-login-password | docker login --username AWS --password-stdin ${AWS_ACCOUNT}.dkr.ecr.us-east-1.amazonaws.com

create-ecr-repo:
	aws ecr create-repository \
    --profile ${PROFILE} \
    --repository-name ${PROJECT_NAME} \
    --image-tag-mutability MUTABLE \
    --tags Key=demo,Value=true \
    --image-scanning-configuration scanOnPush=true
    # Copy the repositoryUri from the output. This is needed in the next step.
    # Initiate the AWS SAM guided deployment using the deploy command
    # ${AWS_ACCOUNT}.dkr.ecr.us-east-1.amazonaws.com/test-sam-prj-addressnet

sam-deploy-initial:
	# sam deploy --guided
	sam deploy \
	--guided \
	--profile ${PROFILE} \
	--config-env ${PROFILE} \
	--region ${AWS_REGION} \
	--stack-name ${PROJECT_NAME} \
	--image-repository ${AWS_ACCOUNT}.dkr.ecr.${AWS_REGION}.amazonaws.com/${PROJECT_NAME}

sam-deploy:
	# sam deploy --guided
	sam deploy \
	--profile ${PROFILE} \
	--config-env ${PROFILE} \
	--region ${AWS_REGION} \
	--stack-name ${PROJECT_NAME}

destroy-ecr:
	aws ecr delete-repository --profile ${PROFILE} --registry-id ${AWS_ACCOUNT} --repository-name ${PROJECT_NAME} --force

destroy-cf:
	aws cloudformation delete-stack --profile ${PROFILE} --stack-name ${PROJECT_NAME}


#################################################################################
# Self Documenting Commands                                                     #
#################################################################################

.DEFAULT_GOAL := help

# Inspired by <http://marmelab.com/blog/2016/02/29/auto-documented-makefile.html>
# sed script explained:
# /^##/:
# 	* save line in hold space
# 	* purge line
# 	* Loop:
# 		* append newline + line to hold space
# 		* go to next line
# 		* if line starts with doc comment, strip comment character off and loop
# 	* remove target prerequisites
# 	* append hold space (+ newline) to line
# 	* replace newline plus comments by `---`
# 	* print line
# Separate expressions are necessary because labels cannot be delimited by
# semicolon; see <http://stackoverflow.com/a/11799865/1968>
.PHONY: help
help:
	@sed -n -e "/^## / { \
		h; \
		s/.*//; \
		:doc" \
		-e "H; \
		n; \
		s/^## //; \
		t doc" \
		-e "s/:.*//; \
		G; \
		s/\\n## /---/; \
		s/\\n/ /g; \
		p; \
	}" ${MAKEFILE_LIST} \
	| LC_ALL='C' sort --ignore-case \
	| awk -F '---' \
		-v ncol=$$(tput cols) \
		-v indent=19 \
		-v col_on="$$(tput setaf 6)" \
		-v col_off="$$(tput sgr0)" \
	'{ \
		printf "%s%*s%s ", col_on, -indent, $$1, col_off; \
		n = split($$2, words, " "); \
		line_length = ncol - indent; \
		for (i = 1; i <= n; i++) { \
			line_length -= length(words[i]) + 1; \
			if (line_length <= 0) { \
				line_length = ncol - indent - length(words[i]) - 1; \
				printf "\n%*s ", -indent, " "; \
			} \
			printf "%s ", words[i]; \
		} \
		printf "\n"; \
	}' \
	| more $(shell test $(shell uname) = Darwin && echo '--no-init --raw-control-chars')
