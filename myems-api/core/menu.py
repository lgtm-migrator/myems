import falcon
import mysql.connector
import simplejson as json

import config
from core.useractivity import user_logger, access_control


class MenuCollection:
    @staticmethod
    def __init__():
        """"Initializes MenuCollection"""
        pass

    @staticmethod
    def on_options(req, resp):
        resp.status = falcon.HTTP_200

    @staticmethod
    def on_get(req, resp):
        cnx = mysql.connector.connect(**config.myems_system_db)
        cursor = cnx.cursor()

        query = (" SELECT id, name, route, parent_menu_id, is_hidden "
                 " FROM tbl_menus "
                 " ORDER BY id ")
        cursor.execute(query)
        rows_menus = cursor.fetchall()

        result = list()
        if rows_menus is not None and len(rows_menus) > 0:
            for row in rows_menus:
                temp = {"id": row[0],
                        "name": row[1],
                        "route": row[2],
                        "parent_menu_id": row[3],
                        "is_hidden": bool(row[4])}

                result.append(temp)

        cursor.close()
        cnx.close()
        resp.text = json.dumps(result)


class MenuItem:
    @staticmethod
    def __init__():
        """"Initializes MenuItem"""
        pass

    @staticmethod
    def on_options(req, resp, id_):
        resp.status = falcon.HTTP_200

    @staticmethod
    def on_get(req, resp, id_):
        if not id_.isdigit() or int(id_) <= 0:
            raise falcon.HTTPError(falcon.HTTP_400, title='API.BAD_REQUEST',
                                   description='API.INVALID_MENU_ID')

        cnx = mysql.connector.connect(**config.myems_system_db)
        cursor = cnx.cursor()

        query = (" SELECT id, name, route, parent_menu_id, is_hidden "
                 " FROM tbl_menus "
                 " WHERE id=%s ")
        cursor.execute(query, (id_,))
        rows_menu = cursor.fetchone()

        result = None
        if rows_menu is not None and len(rows_menu) > 0:
            result = {"id": rows_menu[0],
                      "name": rows_menu[1],
                      "route": rows_menu[2],
                      "parent_menu_id": rows_menu[3],
                      "is_hidden": bool(rows_menu[4])}

        cursor.close()
        cnx.close()
        resp.text = json.dumps(result)

    @staticmethod
    @user_logger
    def on_put(req, resp, id_):
        """Handles PUT requests"""
        access_control(req)
        try:
            raw_json = req.stream.read().decode('utf-8')
        except Exception as ex:
            raise falcon.HTTPError(falcon.HTTP_400, title='API.EXCEPTION', description=str(ex))

        if not id_.isdigit() or int(id_) <= 0:
            raise falcon.HTTPError(falcon.HTTP_400, title='API.BAD_REQUEST',
                                   description='API.INVALID_MENU_ID')

        new_values = json.loads(raw_json)

        if 'is_hidden' not in new_values['data'].keys() or \
                not isinstance(new_values['data']['is_hidden'], bool):
            raise falcon.HTTPError(falcon.HTTP_400, title='API.BAD_REQUEST',
                                   description='API.INVALID_IS_HIDDEN')
        is_hidden = new_values['data']['is_hidden']

        cnx = mysql.connector.connect(**config.myems_system_db)
        cursor = cnx.cursor()
        update_row = (" UPDATE tbl_menus "
                      " SET is_hidden = %s "
                      " WHERE id = %s ")
        cursor.execute(update_row, (is_hidden,
                                    id_))
        cnx.commit()

        cursor.close()
        cnx.close()

        resp.status = falcon.HTTP_200


class MenuChildrenCollection:
    @staticmethod
    def __init__():
        """"Initializes MenuChildrenCollection"""
        pass

    @staticmethod
    def on_options(req, resp, id_):
        resp.status = falcon.HTTP_200

    @staticmethod
    def on_get(req, resp, id_):
        if not id_.isdigit() or int(id_) <= 0:
            raise falcon.HTTPError(falcon.HTTP_400, title='API.BAD_REQUEST',
                                   description='API.INVALID_MENU_ID')

        cnx = mysql.connector.connect(**config.myems_system_db)
        cursor = cnx.cursor()

        query = (" SELECT id, name, route, parent_menu_id, is_hidden "
                 " FROM tbl_menus "
                 " WHERE id = %s ")
        cursor.execute(query, (id_,))
        row_current_menu = cursor.fetchone()
        if row_current_menu is None:
            cursor.close()
            cnx.close()
            raise falcon.HTTPError(falcon.HTTP_404, title='API.NOT_FOUND',
                                   description='API.MENU_NOT_FOUND')

        query = (" SELECT id, name "
                 " FROM tbl_menus "
                 " ORDER BY id ")
        cursor.execute(query)
        rows_menus = cursor.fetchall()

        menu_dict = dict()
        if rows_menus is not None and len(rows_menus) > 0:
            for row in rows_menus:
                menu_dict[row[0]] = {"id": row[0],
                                     "name": row[1]}

        result = dict()
        result['current'] = dict()
        result['current']['id'] = row_current_menu[0]
        result['current']['name'] = row_current_menu[1]
        result['current']['parent_menu'] = menu_dict.get(row_current_menu[3], None)
        result['current']['is_hidden'] = bool(row_current_menu[4])

        result['children'] = list()

        query = (" SELECT id, name, route, parent_menu_id, is_hidden "
                 " FROM tbl_menus "
                 " WHERE parent_menu_id = %s "
                 " ORDER BY id ")
        cursor.execute(query, (id_, ))
        rows_menus = cursor.fetchall()

        if rows_menus is not None and len(rows_menus) > 0:
            for row in rows_menus:
                parent_menu = menu_dict.get(row[3], None)
                meta_result = {"id": row[0],
                               "name": row[1],
                               "parent_menu": parent_menu,
                               "is_hidden": bool(row[4])}
                result['children'].append(meta_result)

        cursor.close()
        cnx.close()
        resp.text = json.dumps(result)


class MenuWebCollection:
    @staticmethod
    def __init__():
        """"Initializes MenuWebCollection"""
        pass

    @staticmethod
    def on_options(req, resp):
        resp.status = falcon.HTTP_200

    @staticmethod
    def on_get(req, resp):
        cnx = mysql.connector.connect(**config.myems_system_db)
        cursor = cnx.cursor()

        query = (" SELECT id, route, parent_menu_id "
                 " FROM tbl_menus "
                 " WHERE parent_menu_id IS NULL AND is_hidden = 0 ")
        cursor.execute(query)
        rows_menus = cursor.fetchall()

        first_level_routes = {}
        if rows_menus is not None and len(rows_menus) > 0:
            for row in rows_menus:
                first_level_routes[row[0]] = {
                    'route': row[1],
                    'children': []
                }

        query = (" SELECT id, route, parent_menu_id "
                 " FROM tbl_menus "
                 " WHERE parent_menu_id IS NOT NULL AND is_hidden = 0 ")
        cursor.execute(query)
        rows_menus = cursor.fetchall()

        if rows_menus is not None and len(rows_menus) > 0:
            for row in rows_menus:
                if row[2] in first_level_routes.keys():
                    first_level_routes[row[2]]['children'].append(row[1])

        result = dict()
        for _id, item in first_level_routes.items():
            result[item['route']] = item['children']

        cursor.close()
        cnx.close()
        resp.text = json.dumps(result)
