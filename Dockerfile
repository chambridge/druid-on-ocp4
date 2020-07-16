# Working from original: https://github.com/apache/druid/blob/master/distribution/docker/Dockerfile

FROM registry.redhat.io/openjdk/openjdk-8-rhel8

COPY ./build /src
WORKDIR /src
RUN mvn -B -ff -q dependency:go-offline \
    install \
    -Pdist,bundle-contrib-exts \
    -Pskip-static-checks,skip-tests \
    -Dmaven.javadoc.skip=true

RUN VERSION=$(mvn -B -q org.apache.maven.plugins:maven-help-plugin:3.1.1:evaluate \
    -Dexpression=project.version -DforceStdout=true \
    ) \
    && tar -zxf ./distribution/target/apache-druid-${VERSION}-bin.tar.gz -C /opt \
    && ln -s /opt/apache-druid-${VERSION} /opt/druid


COPY ./build/distribution/docker/druid.sh /druid.sh

RUN addgroup -S -g 1000 druid \
    && adduser -S -u 1000 -D -H -h /opt/druid -s /bin/sh -g '' -G druid druid \
    && mkdir -p /opt/druid/var \
    && chown -R druid:druid /opt \
    && chmod 775 /opt/druid/var

USER druid
VOLUME /opt/druid/var
WORKDIR /opt/druid

ENTRYPOINT ["/druid.sh"]
