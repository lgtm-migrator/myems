import uuid

import falcon
import mysql.connector
import simplejson as json

import config
from core.useractivity import user_logger, access_control


class EnergyItemCollection:
    @staticmethod
    def __init__():
        """"Initializes EnergyItemCollection"""
        pass

    @staticmethod
    def on_options(req, resp):
        resp.status = falcon.HTTP_200

    @staticmethod
    def on_get(req, resp):
        cnx = mysql.connector.connect(**config.myems_system_db)
        cursor = cnx.cursor()

        query = (" SELECT id, name, uuid "
                 " FROM tbl_energy_categories ")
        cursor.execute(query)
        rows_energy_categories = cursor.fetchall()

        energy_category_dict = dict()
        if rows_energy_categories is not None and len(rows_energy_categories) > 0:
            for row in rows_energy_categories:
                energy_category_dict[row[0]] = {"id": row[0],
                                                "name": row[1],
                                                "uuid": row[2]}

        query = (" SELECT id, name, uuid, energy_category_id "
                 " FROM tbl_energy_items "
                 " ORDER BY id ")
        cursor.execute(query)
        rows = cursor.fetchall()
        cursor.close()
        cnx.close()

        result = list()
        if rows is not None and len(rows) > 0:
            for row in rows:
                energy_category = energy_category_dict.get(row[3], None)
                meta_result = {"id": row[0], "name": row[1], "uuid": row[2],
                               "energy_category": energy_category}
                result.append(meta_result)

        resp.text = json.dumps(result)

    @staticmethod
    @user_logger
    def on_post(req, resp):
        """Handles POST requests"""
        access_control(req)
        try:
            raw_json = req.stream.read().decode('utf-8')
        except Exception as ex:
            raise falcon.HTTPError(falcon.HTTP_400, title='API.ERROR', description=str(ex))

        new_values = json.loads(raw_json)

        if 'name' not in new_values['data'].keys() or \
                not isinstance(new_values['data']['name'], str) or \
                len(str.strip(new_values['data']['name'])) == 0:
            raise falcon.HTTPError(falcon.HTTP_400, title='API.BAD_REQUEST',
                                   description='API.INVALID_ENERGY_ITEM_NAME')

        name = str.strip(new_values['data']['name'])

        if 'energy_category_id' not in new_values['data'].keys() or \
                new_values['data']['energy_category_id'] <= 0:
            raise falcon.HTTPError(falcon.HTTP_400, title='API.BAD_REQUEST',
                                   description='API.INVALID_ENERGY_CATEGORY_ID')
        energy_category_id = new_values['data']['energy_category_id']

        cnx = mysql.connector.connect(**config.myems_system_db)
        cursor = cnx.cursor()

        cursor.execute(" SELECT name "
                       " FROM tbl_energy_items "
                       " WHERE name = %s ", (name,))
        if cursor.fetchone() is not None:
            cursor.close()
            cnx.close()
            raise falcon.HTTPError(falcon.HTTP_400, title='API.BAD_REQUEST',
                                   description='API.ENERGY_ITEM_NAME_IS_ALREADY_IN_USE')

        cursor.execute(" SELECT name "
                       " FROM tbl_energy_categories "
                       " WHERE id = %s ",
                       (energy_category_id,))
        if cursor.fetchone() is None:
            cursor.close()
            cnx.close()
            raise falcon.HTTPError(falcon.HTTP_404, title='API.NOT_FOUND',
                                   description='API.ENERGY_CATEGORY_NOT_FOUND')

        add_value = (" INSERT INTO tbl_energy_items "
                     "    (name, uuid, energy_category_id) "
                     " VALUES (%s, %s, %s) ")
        cursor.execute(add_value, (name,
                                   str(uuid.uuid4()),
                                   energy_category_id))
        new_id = cursor.lastrowid
        cnx.commit()
        cursor.close()
        cnx.close()

        resp.status = falcon.HTTP_201
        resp.location = '/energyitems/' + str(new_id)


class EnergyItemItem:
    @staticmethod
    def __init__():
        """"Initializes EnergyItemItem"""
        pass

    @staticmethod
    def on_options(req, resp, id_):
        resp.status = falcon.HTTP_200

    @staticmethod
    def on_get(req, resp, id_):
        if not id_.isdigit() or int(id_) <= 0:
            raise falcon.HTTPError(falcon.HTTP_400, title='API.BAD_REQUEST',
                                   description='API.INVALID_ENERGY_ITEM_ID')

        cnx = mysql.connector.connect(**config.myems_system_db)
        cursor = cnx.cursor()

        query = (" SELECT id, name, uuid "
                 " FROM tbl_energy_categories ")
        cursor.execute(query)
        rows_energy_categories = cursor.fetchall()

        energy_category_dict = dict()
        if rows_energy_categories is not None and len(rows_energy_categories) > 0:
            for row in rows_energy_categories:
                energy_category_dict[row[0]] = {"id": row[0],
                                                "name": row[1],
                                                "uuid": row[2]}

        query = (" SELECT id, name, uuid, energy_category_id "
                 " FROM tbl_energy_items "
                 " WHERE id =%s ")
        cursor.execute(query, (id_,))
        row = cursor.fetchone()
        cursor.close()
        cnx.close()
        if row is None:
            raise falcon.HTTPError(falcon.HTTP_404, title='API.NOT_FOUND',
                                   description='API.ENERGY_ITEM_NOT_FOUND')

        energy_category = energy_category_dict.get(row[3], None)
        result = {"id": row[0],
                  "name": row[1],
                  "uuid": row[2],
                  "energy_category": energy_category}
        resp.text = json.dumps(result)

    @staticmethod
    @user_logger
    def on_delete(req, resp, id_):
        access_control(req)
        if not id_.isdigit() or int(id_) <= 0:
            raise falcon.HTTPError(falcon.HTTP_400, title='API.BAD_REQUEST',
                                   description='API.INVALID_ENERGY_ITEM_ID')

        cnx = mysql.connector.connect(**config.myems_system_db)
        cursor = cnx.cursor()

        cursor.execute(" SELECT name "
                       " FROM tbl_energy_items "
                       " WHERE id = %s ", (id_,))
        if cursor.fetchone() is None:
            cursor.close()
            cnx.close()
            raise falcon.HTTPError(falcon.HTTP_404, title='API.NOT_FOUND',
                                   description='API.ENERGY_ITEM_NOT_FOUND')

        cursor.execute(" SELECT id "
                       " FROM tbl_meters "
                       " WHERE energy_item_id = %s ", (id_,))
        rows_meters = cursor.fetchall()
        if rows_meters is not None and len(rows_meters) > 0:
            cursor.close()
            cnx.close()
            raise falcon.HTTPError(falcon.HTTP_400,
                                   title='API.BAD_REQUEST',
                                   description='API.ENERGY_ITEM_USED_IN_METER')

        cursor.execute(" SELECT id "
                       " FROM tbl_virtual_meters "
                       " WHERE energy_item_id = %s ", (id_,))
        rows_virtual_meters = cursor.fetchall()
        if rows_virtual_meters is not None and len(rows_virtual_meters) > 0:
            cursor.close()
            cnx.close()
            raise falcon.HTTPError(falcon.HTTP_400,
                                   title='API.BAD_REQUEST',
                                   description='API.ENERGY_ITEM_USED_IN_VIRTUAL_METER')

        cursor.execute(" SELECT id "
                       " FROM tbl_offline_meters "
                       " WHERE energy_item_id = %s ", (id_,))
        rows_offline_meters = cursor.fetchall()
        if rows_offline_meters is not None and len(rows_offline_meters) > 0:
            cursor.close()
            cnx.close()
            raise falcon.HTTPError(falcon.HTTP_400,
                                   title='API.BAD_REQUEST',
                                   description='API.ENERGY_ITEM_USED_IN_OFFLINE_METER')

        cursor.execute(" DELETE FROM tbl_energy_items WHERE id = %s ", (id_,))
        cnx.commit()

        cursor.close()
        cnx.close()
        resp.status = falcon.HTTP_204

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
                                   description='API.INVALID_ENERGY_ITEM_ID')

        new_values = json.loads(raw_json)
        if 'name' not in new_values['data'].keys() or \
                not isinstance(new_values['data']['name'], str) or \
                len(str.strip(new_values['data']['name'])) == 0:
            raise falcon.HTTPError(falcon.HTTP_400, title='API.BAD_REQUEST',
                                   description='API.INVALID_ENERGY_ITEM_NAME')

        name = str.strip(new_values['data']['name'])

        if 'energy_category_id' not in new_values['data'].keys() or new_values['data']['energy_category_id'] <= 0:
            raise falcon.HTTPError(falcon.HTTP_400, title='API.BAD_REQUEST',
                                   description='API.INVALID_ENERGY_CATEGORY_ID')
        energy_category_id = new_values['data']['energy_category_id']

        cnx = mysql.connector.connect(**config.myems_system_db)
        cursor = cnx.cursor()

        cursor.execute(" SELECT name "
                       " FROM tbl_energy_items "
                       " WHERE id = %s ", (id_,))
        if cursor.fetchone() is None:
            cursor.close()
            cnx.close()
            raise falcon.HTTPError(falcon.HTTP_404, title='API.NOT_FOUND',
                                   description='API.ENERGY_ITEM_NOT_FOUND')

        cursor.execute(" SELECT name "
                       " FROM tbl_energy_items "
                       " WHERE name = %s AND id != %s ", (name, id_))
        if cursor.fetchone() is not None:
            cursor.close()
            cnx.close()
            raise falcon.HTTPError(falcon.HTTP_400, title='API.BAD_REQUEST',
                                   description='API.ENERGY_ITEM_NAME_IS_ALREADY_IN_USE')

        cursor.execute(" SELECT name "
                       " FROM tbl_energy_categories "
                       " WHERE id = %s ",
                       (energy_category_id,))
        if cursor.fetchone() is None:
            cursor.close()
            cnx.close()
            raise falcon.HTTPError(falcon.HTTP_404, title='API.NOT_FOUND',
                                   description='API.ENERGY_CATEGORY_NOT_FOUND')

        update_row = (" UPDATE tbl_energy_items "
                      " SET name = %s, energy_category_id = %s "
                      " WHERE id = %s ")
        cursor.execute(update_row, (name,
                                    energy_category_id,
                                    id_,))
        cnx.commit()
        cursor.close()
        cnx.close()
        resp.status = falcon.HTTP_200

