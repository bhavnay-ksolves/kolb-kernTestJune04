/* @odoo-module */

import { AttachmentUploadService } from "@mail/core/common/attachment_upload_service";
import { patch } from "@web/core/utils/patch";


patch(AttachmentUploadService.prototype, {
    /*
    * Re-write to pass thread folder for the upload controller
    */
    _buildFormData(formData, tmpURL, thread, composer, tmpId, options) {
        if (thread && thread.cloudsFolderId && !composer) {
            formData.append("clouds_folder_id", parseInt(thread.cloudsFolderId));
        };
        return super._buildFormData(...arguments);
    },
    /*
    * Re-write to recalculate attachment after uploading if folder is selected
    */
    async _upload(thread, composer, file, options, tmpId, tmpURL) {
        const res = await super._upload(...arguments);
        if (thread && thread.cloudsFolderId) {
            thread.fetchFolderAttachments();
        };
        return res;
    },
});
