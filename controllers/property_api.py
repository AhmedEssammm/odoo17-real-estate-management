import json
import math
from urllib.parse import parse_qs


from odoo import http
from odoo.http import request


def valid_response(data, status, pagination_info):
    response_body = {
        "data": data,
        "code": status,
        "message": "success",
    }
    if pagination_info:
        response_body['pagination_info'] = pagination_info
    return request.make_json_response(data=response_body, status=status)

def invalid_response(error, status):
    response_body = {
        "error": error,
        "code": status,
        "message": "error",
    }
    return request.make_json_response(data=response_body, status=status)

class PropertyApi(http.Controller):
    # @http.route("/v1/property", methods=["POST"], type="http", auth="none", csrf=False)
    # def post_property(self):
    #     args = request.httprequest.data.decode()
    #     vals = json.loads(args)
    #     if not vals.get('name'):
    #         return invalid_response({
    #             "error": "Property Name is required",
    #         }, 400)
    #     try:
    #         res = request.env['property'].sudo().create(vals)
    #         if res:
    #             return valid_response({
    #                 "message": "Property successfully created",
    #                 "id": res.id,
    #                 "name": res.name,
    #             }, 201)
    #     except Exception as e:
    #         return (invalid_response({
    #             "error": e,
    #         }, 400)

    @http.route("/v1/property", methods=["POST"], type="http", auth="none", csrf=False)
    def post_property(self):
        args = request.httprequest.data.decode()
        vals = json.loads(args)
        if not vals.get('name'):
            return invalid_response({
                "error": "Property Name is required",
            }, 400)
        try:
            cr = request.env.cr
            columns = ', '.join(vals.keys())
            values = ', '.join(['%s'] * len(vals))
            query = f"""INSERT INTO property ({columns}) VALUES ({values}) RETURNING id, name, postcode"""
            cr.execute(query, tuple(vals.values()))
            res = cr.fetchone()
            print(res)
            if res:
                return request.make_json_response({
                    "message": "Property successfully created",
                    "id": res[0],
                    "name": res[1],
                    "postcode": res[2],
                }, 201)
        except Exception as e:
            return invalid_response({
                "error": e,
            }, 400)

    @http.route("/v1/property/json", methods=["POST"], type="json", auth="none", csrf=False)
    def post_property_json(self):
        args = request.httprequest.data.decode()
        vals = json.loads(args)
        res = request.env['property'].sudo().create(vals)
        if res:
            return {
                "message": "Property successfully created"
            }

    @http.route("/v1/property/<int:property_id>", methods=["PUT"], type="http", auth="none", csrf=False)
    def update_property(self, property_id):
        try:
            property_id = request.env['property'].sudo().search([('id', '=', property_id)])
            if not property_id:
                return invalid_response({
                    "error": "Property not found",
                }, 404)
            args = request.httprequest.data.decode()
            vals = json.loads(args)
            property_id.write(vals)
            return valid_response({
                "message": "Property successfully updated",
                "id": property_id.id,
                "name": property_id.name,
            }, 200)
        except Exception as e:
            return invalid_response({
                "error": e,
            }, 400)

    @http.route("/v1/property/<property_id>", methods=["GET"], type="http", auth="none", csrf=False)
    def get_property(self, property_id):
        try:
            property_id = request.env['property'].sudo().search([('id', '=', property_id)])
            if not property_id:
                return invalid_response({
                    "error": "Property not found",
                }, 404)
            return valid_response({
                "message": "Property successfully retrieved",
                "id": property_id.id,
                "name": property_id.name,
                "ref": property_id.ref,
                "description": property_id.description,
                "bedrooms": property_id.bedrooms,
            }, 200)
        except Exception as e:
            return invalid_response({
                "error": e,
            }, 400)

    @http.route("/v1/property/<property_id>", methods=["DELETE"], type="http", auth="none", csrf=False)
    def delete_property(self, property_id):
        property_id = request.env['property'].sudo().search([('id', '=', property_id)])
        try:
            if not property_id:
                return invalid_response({
                    "error": "Property not found",
                }, 404)
            property_id.unlink()
            return valid_response({
                "message": "Property successfully deleted",
            }, 200)
        except Exception as e:
            return invalid_response({
                "error": e,
            }, 400)

    @http.route("/v1/properties", methods=["GET"], type="http", auth="none", csrf=False)
    def get_property_list(self):
        try:
            params = parse_qs(request.httprequest.query_string.decode('utf-8'))
            property_domain = []
            page = offset = None
            limit = 5
            if params:
                if params.get('limit'):
                    limit = int(params['limit'][0])
                if params.get('page'):
                    page = int(params['page'][0])
            if page:
                offset = (page * limit) - limit
            if params.get('state'):
                property_domain += [('state', '=', params.get('state')[0])]
            property_ids = request.env['property'].sudo().search(property_domain, offset=offset, limit=limit, order='id desc')
            property_count = request.env['property'].sudo().search_count(property_domain)
            print(offset)
            print(page)
            print(limit)
            print(property_ids)
            print(property_count)
            if not property_ids:
                return invalid_response({
                    "error": "Properties not found",
                }, 404)
            return valid_response([{
                "id": property_id.id,
                "name": property_id.name,
                "ref": property_id.ref,
                "description": property_id.description,
                "bedrooms": property_id.bedrooms,
            } for property_id in property_ids],
                200,
                {
                'page': page if page else 1,
                'limit': limit,
                'pages': math.ceil(property_count / limit) if limit else 1,
                'count': property_count
            })
        except Exception as e:
            return invalid_response({
                "error": e,
            }, 400)