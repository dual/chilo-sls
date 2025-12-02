from chilo_sls.apigateway.requirements import requirements

@requirements()
def get(request, response):
    response.body = {'router_mapping_optional': True}
    return response
