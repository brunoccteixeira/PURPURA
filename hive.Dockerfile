# Start from the official Hive image
FROM apache/hive:3.1.3

# Hadoop/Hive needs specific versions of these JARs to talk to S3.
# These versions are known to be compatible.
ARG HADOOP_AWS_JAR_VERSION=3.3.4
ARG AWS_JAVA_SDK_VERSION=1.12.367

# Switch to the root user to install packages and download files
USER root

# Update package lists and install required tools (wget for downloading, net-tools for healthcheck)
RUN apt-get update && apt-get install -y wget net-tools

# Download the required JARs into Hive's library folder (as root)
RUN wget https://repo1.maven.org/maven2/org/apache/hadoop/hadoop-aws/${HADOOP_AWS_JAR_VERSION}/hadoop-aws-${HADOOP_AWS_JAR_VERSION}.jar -P /opt/hive/lib/ && \
    wget https://repo1.maven.org/maven2/com/amazonaws/aws-java-sdk-bundle/${AWS_JAVA_SDK_VERSION}/aws-java-sdk-bundle-${AWS_JAVA_SDK_VERSION}.jar -P /opt/hive/lib/

# Switch back to the default hive user for runtime
USER hive

