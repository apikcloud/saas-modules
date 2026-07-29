from odoo import _, http
from odoo.http import request, Response, db_list
from odoo.tools import config

from odoo.addons.web.controllers.main import ensure_db, set_cookie_and_redirect, Home

import logging
_logger = logging.getLogger(__name__)


class ImpersonateController(Home):
    @http.route(
        "/impersonate", type="http", auth="none", csrf=False, methods=["GET", "POST"]
    )
    def impersonate(self, redirect=None, **kw):
        _logger.info("Impersonate")
        if 'fleet_access_token' not in request.params:
            return Response("Missing param fleet_access_token", status=400)
        if 'uid' not in request.params:
            return Response("Missing param uid", status=400) 
        
        ensure_db()
        _logger.info("Ensure db")
        conf_access_fleet_token = config.get('fleet_access_token', None)
        _logger.info(conf_access_fleet_token)
        param_access_fleet_token = request.params['fleet_access_token']
        _logger.info(param_access_fleet_token)
        
        request.params["login_success"] = False
        conf_access_fleet_token = config.get("fleet_access_token", None)
        param_access_fleet_token = request.params["fleet_access_token"]

        if conf_access_fleet_token != param_access_fleet_token:
            return Response("Wrong token", status=401)
            
        dbs = db_list(force=True)
        _logger.info("DBs")
        _logger.info(dbs)
        uid = request.session.uid = int(request.params['uid'])
        user = http.request.env['res.users'].browse(uid)
        request.session.db = dbs[0]
        request.session.uid = uid
        request.session.login = user.login
        request.session.session_token = user._compute_session_token(request.session.sid)
        
        request.env.registry.clear_caches()

        request.params["login_success"] = True
        # Only usefull because Odoo verifies if the password is 'admin' to warn the user.
        # It throws if no password is provided.
        request.params["password"] = "x"
        return http.redirect_with_hash(redirect or '/web')
