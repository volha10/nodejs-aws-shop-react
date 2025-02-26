import os
from aws_cdk import (
    CfnOutput,
    Stack,
    aws_s3 as s3,
    aws_s3_deployment as s3_deployment,
    aws_cloudfront as cloudfront,
    aws_cloudfront_origins as cloudfront_origins,
    RemovalPolicy,

)
from constructs import Construct

class MyWebAppStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Create S3 to store website files
        website_bucket = s3.Bucket(
            self, 
            "WebsiteBucket",
            block_public_access=s3.BlockPublicAccess.BLOCK_ALL,
            encryption=s3.BucketEncryption.S3_MANAGED,
            enforce_ssl=True,
            removal_policy=RemovalPolicy.DESTROY,
            auto_delete_objects=True,
        )

        # Create CloudFront distribution
        distribution = cloudfront.Distribution(
            self, 
            "Distribution",
            default_behavior=cloudfront.BehaviorOptions(
                origin=cloudfront_origins.S3Origin(website_bucket),
                viewer_protocol_policy=cloudfront.ViewerProtocolPolicy.REDIRECT_TO_HTTPS,
                cache_policy=cloudfront.CachePolicy.CACHING_OPTIMIZED,
            ),
            default_root_object="index.html",
            error_responses=[
                cloudfront.ErrorResponse(
                    http_status=404,
                    response_http_status=200,
                    response_page_path="/index.html"
                )
            ]
        )

        # Deploy site content to S3

        s3_deployment.BucketDeployment(
            self, 
            "BucketDeployment",
            sources=[s3_deployment.Source.asset(os.path.join(os.path.dirname(__file__), "../../dist"))],
            destination_bucket=website_bucket,
            distribution=distribution,
            distribution_paths=['/*'],

        )

        # Output the Cloudfront URL
        CfnOutput(
            self, 
            "DistributionDomainName",
            value=distribution.distribution_domain_name,
            description="Website URL",
        )


