/* @odoo-module */

import { Thread } from "@mail/core/common/thread_model";
import { patch } from "@web/core/utils/patch";
import { rpc } from "@web/core/network/rpc";


patch(Thread.prototype, {
    /*
    * The method to refresh attachment box when checked folder is changed
    */
    async refreshFolderAttachments(folderDomain, cloudsFolderId) {
        Object.assign(this, { folderDomain: folderDomain, cloudsFolderId: cloudsFolderId});
        this.fetchFolderAttachments();
    },
    /*
    * The method to get attachments linked to the currently selected folder
    */
    async fetchFolderAttachments() {
        const { data, attachments }  = await rpc(
            "/cloud_base/attachments/data",
            {
                thread_id: this.id,
                thread_model: this.model,
                checked_folder: this.cloudsFolderId || false,
                folder_domain: this.folderDomain || [],
            },
        );
        this.store.insert(data, { html: true });
        this.store.Attachment.insert(attachments);
        this.update({ attachments: attachments });
    },
});
