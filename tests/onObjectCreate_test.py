import os
import json
import requests


def presigned_url_lambda_apigw_url() -> str:
    with open(f"../pulumi_output.json", "r") as read_file:
        pulumi_output = json.load(read_file)

    api_id = pulumi_output["api"]["restAPI"]["id"]
    api_stage = pulumi_output["api"]["stage"]["stageName"]
    the_sauce = ".execute-api.localhost.localstack.cloud:4566/"
    return "http://" + api_id + the_sauce + api_stage + "/get_presigned_url"


def change_host_of_url_to_localhost(url: str):
    # TODO prepend bucket to end doesn't work
    # url = "http://" + os.environ["LOCALSTACK_HOSTNAME"] + ":4566" + url.split(":4566")[1]
    # TODO add bucket in url like in PR logs doesn't work
    url = "http://" + url.split(":4566/")[1] + "." + os.environ["LOCALSTACK_HOSTNAME"] + ":4566"
    print(url)
    return url


def format_res(resp) -> dict:
    resp_dict = {
        "status": resp.status_code,
        "url": resp.url,
        "redirect": resp.is_redirect,
        "headers": resp.headers,
    }
    try:
        resp_dict["content"] = json.loads(resp.content)
        resp_dict["links"] = resp.links
    except Exception:
        resp_dict["content"] = resp.content

    return resp_dict


def test_error_no_files():
    # get the apigw url for s3_create_presigned_url_lambda
    presigned_post_url = presigned_url_lambda_apigw_url()
    # query string passes in metadata into lambda for presigned post
    query_string = {
        "action": "upload",
        "file_name": "demo_file.csv",
        "content_type": "csv",
    }
    # get presigned url
    res = format_res(requests.get(presigned_post_url, params=query_string))

    # parse out url & fields
    post_url = res["content"]["data"]["url"]
    post_fields = res["content"]["data"]["fields"]
    # add file as last in post fields
    files = {"file" : open(f"../{query_string['file_name']}", "rb")}

    # make post request to presigned url | should trigger lambda & display logs
    res2 = format_res(requests.post(change_host_of_url_to_localhost(post_url), data=post_fields, files=files))
    print(res2)
    # TODO doesn't show in localstack logs nor lambda specific logs | no lambda log output
    # run from root -- make get-logs-s3-on-object-created -- to see lambda specific logs
    # run from root -- make get-logs-aws -- to see localstack logs


def test_error_with_files():
    # get the apigw url for s3_create_presigned_url_lambda
    presigned_post_url = presigned_url_lambda_apigw_url()
    # query string passes in metadata into lambda for presigned post
    query_string = {
        "action": "upload",
        "file_name": "demo_file.csv",
        "content_type": "csv",
    }
    # get presigned url
    res = format_res(requests.get(presigned_post_url, params=query_string))

    # parse out url & fields
    post_url = res["content"]["data"]["url"]
    post_fields = res["content"]["data"]["fields"]
    # add file as last in post fields
    files = {
        "file": open(f"../{query_string['file_name']}", "rb")
    }

    # make post request to presigned url | should trigger lambda & display logs
    res2 = format_res(requests.post(change_host_of_url_to_localhost(post_url), data=post_fields, files=files))
    print(res2)
