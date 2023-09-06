#!/bin/bash

# AWS variables
AWS_PROFILE=default
AWS_REGION=eu-west-2
# project variables
PROJECT_NAME=eks-practicepractice

# the directory containing the script file
dir="$(cd "$(dirname "$0")"; pwd)"
cd "$dir"

log()   { echo -e "\e[30;47m $(echo "$1" | tr '[:lower:]' '[:upper:]') \e[0m ${@:2}"; }        # Convert $1 to uppercase
info()  { echo -e "\e[48;5;28m $(echo "$1" | tr '[:lower:]' '[:upper:]') \e[0m ${@:2}"; }      # Convert $1 to uppercase
warn()  { echo -e "\e[48;5;202m $(echo "$1" | tr '[:lower:]' '[:upper:]') \e[0m ${@:2}" >&2; } # Convert $1 to uppercase
error() { echo -e "\e[48;5;196m $(echo "$1" | tr '[:lower:]' '[:upper:]') \e[0m ${@:2}" >&2; } #
# log $1 in underline then $@ then a newline
under() {
    local arg=$1
    shift
    echo -e "\033[0;4m${arg}\033[0m ${@}"
    echo
}

usage() {
    under usage 'call the Makefile directly: make dev
      or invoke this file directly: ./make.sh dev'
}

# install eksctl if missing (no update)
install-eksctl() {
    if [[ -z $(command -v eksctl) ]]; then
        log install eksctl
        warn warn sudo is required
	brew tap weaveworks/tap
	brew install eksctl
    else
        log skip eksctl already installed
    fi
}

# install yq if missing (no update)
install-yq() {
    if [[ -z $(which yq) ]]
    then
        log install yq
        warn warn sudo is required
	brew install yq

    else
        log skip yq already installed
    fi

    if [[ -z $(which jq) ]]
    then
        log install jq
	brew install jq
    else
        log skip jq already installed
    fi
}

# install kubectl if missing (no update)
install-kubectl() {
    if [[ -z $(which kubectl) ]]
    then
        log install eksctl
        warn warn sudo is required
        local VERSION=$(curl --silent https://storage.googleapis.com/kubernetes-release/release/stable.txt)
        cd /usr/local/bin
        sudo curl https://storage.googleapis.com/kubernetes-release/release/$VERSION/bin/linux/amd64/kubectl \
            --progress-bar \
            --location \
            --remote-name
        sudo chmod +x kubectl
    else
        log skip kubectl already installed
    fi
}


create-env() {
    [[ -f "$dir/.env" ]] && { log skip .env file already exists; return; }
    info create .env file
    # check if user already exists (return something if user exists, otherwise return nothing)
    local exists=$(aws iam list-user-policies \
        --user-name $PROJECT_NAME \
        --profile $AWS_PROFILE \
        2>/dev/null)
        
    [[ -n "$exists" ]] && { error abort user $PROJECT_NAME already exists; return; }

    # create a user named $PROJECT_NAME
    log create iam user $PROJECT_NAME
    aws iam create-user \
        --user-name $PROJECT_NAME \
        --profile $AWS_PROFILE \
        1>/dev/null

    aws iam attach-user-policy \
        --user-name $PROJECT_NAME \
        --policy-arn arn:aws:iam::aws:policy/PowerUserAccess \
        --profile $AWS_PROFILE

    local key=$(aws iam create-access-key \
        --user-name $PROJECT_NAME \
        --query 'AccessKey.{AccessKeyId:AccessKeyId,SecretAccessKey:SecretAccessKey}' \
        --profile $AWS_PROFILE \
        2>/dev/null)

    local AWS_ACCESS_KEY_ID=$(echo "$key" | jq '.AccessKeyId' --raw-output)
    log AWS_ACCESS_KEY_ID $AWS_ACCESS_KEY_ID
    
    local AWS_SECRET_ACCESS_KEY=$(echo "$key" | jq '.SecretAccessKey' --raw-output)
    log AWS_SECRET_ACCESS_KEY $AWS_SECRET_ACCESS_KEY

    # create ECR repository
    local repo=$(aws ecr describe-repositories \
        --repository-names $PROJECT_NAME \
        --region $AWS_REGION \
        --profile $AWS_PROFILE \
        2>/dev/null)
    if [[ -z "$repo" ]]
    then
        log ecr create-repository $PROJECT_NAME
        local ECR_REPOSITORY=$(aws ecr create-repository \
            --repository-name $PROJECT_NAME \
            --region $AWS_REGION \
            --profile $AWS_PROFILE \
            --query 'repository.repositoryUri' \
            --output text)
        log ECR_REPOSITORY $ECR_REPOSITORY
    fi

    # envsubst tips : https://unix.stackexchange.com/a/294400
    # create .env file
    cd "$dir"
    # export variables for envsubst
    export AWS_ACCESS_KEY_ID
    export AWS_SECRET_ACCESS_KEY
    export ECR_REPOSITORY
    envsubst < .env.tmpl > .env

    info created file .env
}

# install eksctl + kubectl + yq, create aws user + ecr repository
setup() {
    install-eksctl
    install-kubectl
    install-yq
    create-env
}

# build the production image locally
build() {
    cd "$dir/site"
    local VERSION=$(jq --raw-output '.version' package.json)
    log build $PROJECT_NAME:$VERSION
    docker image build \
        --tag $PROJECT_NAME:latest \
        --tag $PROJECT_NAME:$VERSION \
        .
}

# run the latest built production image on localhost
run() {
    [[ -n $(docker ps --format '{{.Names}}' | grep $PROJECT_NAME) ]] \
        && { error error container already exists; return; }
    log run $PROJECT_NAME on http://localhost:80
    docker run \
        --detach \
        --name $PROJECT_NAME \
        --publish 80:$WEBSITE_PORT \
        $PROJECT_NAME
}

# remove the running container
rm() {
    [[ -z $(docker ps --format '{{.Names}}' | grep $PROJECT_NAME) ]]  \
        && { warn warn no running container found; return; }
    docker container rm \
        --force $PROJECT_NAME
}

# create the EKS cluster
cluster-create() {
    # check if cluster already exists (return something if the cluster exists, otherwise return nothing)
    local exists=$(aws eks describe-cluster \
        --name $PROJECT_NAME \
        --profile $AWS_PROFILE \
        --region $AWS_REGION \
        2>/dev/null)
        
    [[ -n "$exists" ]] && { error abort cluster $PROJECT_NAME already exists; return; }

    # create a cluster named $PROJECT_NAME
    log create eks cluster $PROJECT_NAME

    eksctl create cluster \
        --name $PROJECT_NAME \
        --region $AWS_REGION \
        --managed \
        --node-type t2.micro \
        --nodes 1 \
        --profile $AWS_PROFILE
}

# create kubectl EKS configuration
cluster-create-config() {
    log create kubeconfig.yaml
    CONTEXT=$(kubectl config current-context)
    log context $CONTEXT
    kubectl config view --context=$CONTEXT --minify > kubeconfig.yaml

    log inject certificate
    # yq tips: https://mikefarah.gitbook.io/yq/usage/path-expressions#with-prefixes
    CERTIFICATE=$(yq eval '.clusters[] | select(.name == "eks-practicepractice.eu-west-2.eksctl.io") | .cluster.certificate-authority-data' $HOME/.kube/config)
    log certificate CERTIFICATE
    yq e ".clusters[0].cluster.certificate-authority-data = \"$CERTIFICATE\"" -i kubeconfig.yaml

    log delete env values
    yq e 'del(.users[0].user.exec.env)' kubeconfig.yaml

    log create KUBECONFIG file
    cat kubeconfig.yaml | base64 > KUBECONFIG

    log configmap get configmap aws-auth file
    kubectl -n kube-system get configmap aws-auth -o yaml > aws-auth-configmap.yaml

    # root account id
    local ACCOUNT_ID=$(aws sts get-caller-identity \
        --query 'Account' \
        --profile $AWS_PROFILE \
        --output text)

    warn warn 'inject the lines below in aws-auth-configmap.yaml'
    echo "mapUsers: |
    - userarn: arn:aws:iam::$ACCOUNT_ID:user/$PROJECT_NAME
      username: $PROJECT_NAME
      groups:
        - system:masters"
}

# apply kubectl EKS configuration
cluster-apply-config() {
    # check if data.mapUsers is configured (return something if data.mapUsers is configured, otherwise return nothing)
    local exists=$(yq e .data.mapUsers aws-auth-configmap.yaml)
    [[ -z "$exists" ]] && { error abort data.mapUsers not configured in aws-auth-configmap.yaml; return; }

    log apply aws-auth-configmap.yaml
    kubectl -n kube-system apply -f aws-auth-configmap.yaml

    log test kubectl get ns
    source "$dir/.env"
    export AWS_ACCESS_KEY_ID
    export AWS_SECRET_ACCESS_KEY
    kubectl --kubeconfig kubeconfig.yaml get ns
}

# get the cluster ELB URL
cluster-elb() {
    kubectl get svc \
        --namespace $PROJECT_NAME \
        --output jsonpath="{.items[?(@.metadata.name=='website')].status.loadBalancer.ingress[].hostname}"
}

# delete the EKS cluster
cluster-delete() {
    eksctl delete cluster \
        --name $PROJECT_NAME \
        --region $AWS_REGION \
        --profile $AWS_PROFILE
}



# if `$1` is a function, execute it. Otherwise, print usage
# compgen -A 'function' list all declared functions
# https://stackoverflow.com/a/2627461
FUNC=$(compgen -A 'function' | grep $1)
[[ -n $FUNC ]] && { info execute $1; eval $1; } || usage;
exit 0
