/** @odoo-module **/

import { Domain } from "@web/core/domain";
import { SearchModel } from "@web/search/search_model";


export class CloudManagerSearchModel extends SearchModel {
    /*
    * Overwrite to introduce jsTreeDomain
    */
    setup(services) {
        this.jsTreeDomain = [];
        super.setup(...arguments);
    }
    /*
    * Overwrite to add our jsTree
    */
    _getDomain(params = {}) {
        const domain =  super._getDomain(...arguments);
        const result = Domain.and([domain, this.jsTreeDomain]);
        return params.raw ? result : result.toList();
    }
    /*
    * The method to save received jsTree domain
    */
    toggleJSTreeDomain(domain) {
        this.jsTreeDomain = domain;
        this._notify();
    }
}
