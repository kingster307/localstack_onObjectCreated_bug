import json
import requests


def presigned_url_lambda_apigw_url() -> str:
    with open(f"../pulumi_output.json", "r") as read_file:
        pulumi_output = json.load(read_file)

    api_id = pulumi_output["api"]["restAPI"]["id"]
    api_stage = pulumi_output["api"]["stage"]["stageName"]
    the_sauce = ".execute-api.localhost.localstack.cloud:4566/"
    return "http://" + api_id + the_sauce + api_stage + "/get_presigned_url"


def change_host_of_url_to_localhost(url: str, remove_protocol: bool = True):
    return "http://localhost:" + url.split("://")[-1].split(":")[-1]


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


def test_error():
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
    post_fields["file"] = open(f"../{query_string['file_name']}", "rb")

    # make post request to presigned url | should trigger lambda & display logs
    res2 = format_res(requests.post(change_host_of_url_to_localhost(post_url), data=post_fields))
    # run make get-logs-aws from root
