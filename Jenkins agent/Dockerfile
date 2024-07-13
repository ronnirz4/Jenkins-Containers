FROM amazonlinux:2 as installer

# Install AWS CLI
RUN curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip" \
 && yum update -y \
 && yum install -y unzip \
 && unzip awscliv2.zip \
 && ./aws/install --bin-dir /aws-cli-bin/ \
 && rm -rf awscliv2.zip

# Install Snyk CLI
RUN mkdir /snyk && cd /snyk \
   && curl https://static.snyk.io/cli/v1.666.0/snyk-linux -o snyk \
   && chmod +x snyk

# Install Python and pip, then scikit-learn
RUN yum install -y python3 python3-pip \
 && pip3 install scikit-learn

# Switch to the Jenkins agent image
FROM jenkins/agent
COPY --from=installer /usr/local/aws-cli/ /usr/local/aws-cli/
COPY --from=installer /aws-cli-bin/ /usr/local/bin/
COPY --from=installer /snyk/ /usr/local/bin/
COPY --from=installer /snyk/ /usr/bin/
USER jenkins
