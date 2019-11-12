FROM python:3.7-alpine3.8

RUN apk --update add --no-cache \
    nodejs \
    npm

RUN pip install awscli boto3
RUN npm install -g serverless

RUN mkdir /root/work
WORKDIR /root/work

ENTRYPOINT ["serverless"]
CMD ["--version"]
