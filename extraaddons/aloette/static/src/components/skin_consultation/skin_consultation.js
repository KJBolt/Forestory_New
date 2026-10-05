/** @odoo-module **/

import {registry} from '@web/core/registry';
import { Component, useState } from "@odoo/owl";
import {useService} from "@web/core/utils/hooks";


export class SkinConsultation extends Component {
    static template = 'aloette.SkinConsultation';
    static props = {};

    setup() {
        this.orm = useService('orm');
        this.notification = useService('notification');
        this.rpc = useService('rpc');
        this.action = useService('action');

        this.state = useState({
            likes: [],
            improvements: [],
            customers: [],
            customerId: null,
            vascularity: null,
            skinTexture: null,
            pigmentation: null,
            hydration: null,
            sebaceousActivity: null,

            likeComment: '',
            improveComment: '',
            vascularityComment: '',
            skinTextureComment: '',
            pigmentationComment: '',
            hydrationComment: '',
            sebaceousActivityComment: '',

            // Stepper
            currentStep: 1,
            totalSteps: 4,
        });

        // Fetch contacts from res.partner
        this.rpc('/web/dataset/call_kw', {
            model: 'res.partner',
            method: 'search_read',
            args: [[], ['id', 'name']],
            kwargs: {},
        }).then(result => {
            this.state.customers = result;
        });

        this.skinAttributes = [
            { id: 1, name: 'Texture' },
            { id: 2, name: 'Complexion' },
            { id: 3, name: 'Moisture Content' },
            { id: 4, name: 'Other' }
        ];

        this.vascularityOptions = [
            { id: 1, name: 'Hypo' },
            { id: 2, name: 'Normal' },
            { id: 3, name: 'Hyper' },
            { id: 4, name: 'Other' }
        ];

        this.skinTextureOptions = [
            { id: 1, name: 'Thin' },
            { id: 2, name: 'Medium' },
            { id: 3, name: 'Thick' },
            { id: 4, name: 'Other' }
        ];

        this.depthOfPigmentationOptions = [
            { id: 1, name: 'Superficial' },
            { id: 2, name: 'Dermal' },
            { id: 3, name: 'Both' },
            { id: 4, name: 'Other' }
        ];

        this.hydrationLevelOptions = [
            { id: 1, name: 'Extreme Dehydrated' },
            { id: 2, name: 'Dehydrated' },
            { id: 3, name: 'Normal' },
            { id: 4, name: 'Other' }
        ];

        this.sebaceousActivityOptions = [
            { id: 1, name: 'Hypo' },
            { id: 2, name: 'Normal' },
            { id: 3, name: 'Hyper' },
            { id: 4, name: 'Other' }
        ];
    }

    updateLikes(id, checked) {
        if (checked) {
            this.state.likes.push(id);
        } else {
            const index = this.state.likes.indexOf(id);
            if (index > -1) {
                this.state.likes.splice(index, 1);
            }
        }
        // Clear comment if 'Other' is unselected
        if (id === 4 && !checked) {
            this.state.likeComment = '';
        }
    }

    updateImprovements(id, checked) {
        if (checked) {
            this.state.improvements.push(id);
        } else {
            const index = this.state.improvements.indexOf(id);
            if (index > -1) {
                this.state.improvements.splice(index, 1);
            }
        }

        // Clear comment if 'Other' is unselected
        if (id === 4 && !checked) {
            this.state.improveComment = '';
        }
    }

    updateVascularity(optionId) {
        this.state.vascularity = optionId;
        if (optionId != 4) {
            this.state.vascularityComment = '';
        }
    }

    updateSkinTexture(optionId) {
        this.state.skinTexture = optionId;
        if (optionId != 4) {
            this.state.skinTextureComment = '';
        }
    }

    updatePigmentation(optionId) {
        this.state.pigmentation = optionId;
        if (optionId != 4) {
            this.state.pigmentationComment = '';
        }
    }

    updateHydration(optionId) {
        this.state.hydration = optionId;
            if (optionId != 4) {
            this.state.hydrationComment = '';
        }
    }

    updateSebaceousActivity(optionId) {
        this.state.sebaceousActivity = optionId;
        if (optionId != 4) {
            this.state.sebaceousActivityComment = '';
        }
    }

    // Redirect to Contacts
    redirectToContacts(ev) {
        const value = ev.target.value;
        if (value == 'create') {
            this.action.doAction({
                type: "ir.actions.act_window",
                res_model: "res.partner",
                view_mode: "form",
                views: [[false, "form"]],
                target: "current", // or "new" for a popup
            });
        }
    }

    // Stepper navigations
    nextStep() {
        if (this.state.currentStep < this.state.totalSteps) {
            this.state.currentStep += 1;
        }
    }

    prevStep() {
        if (this.state.currentStep > 1) {
            this.state.currentStep -= 1;
        }
    }

    // Check if fields are not empty
    isFormValid() {
        return (
            this.state.likes.length > 0 &&
            this.state.improvements.length > 0 &&
            this.state.vascularity != undefined &&
            this.state.skinTexture != undefined &&
            this.state.pigmentation != undefined &&
            this.state.hydration != undefined &&
            this.state.sebaceousActivity != undefined
        );
    }

    emptyFields() {
        this.state.likes = [];
        this.state.improvements = [];
        this.state.vascularity = null;
        this.state.skinTexture = null;
        this.state.pigmentation = null;
        this.state.hydration = null;
        this.state.sebaceousActivity = null;
        this.state.likeComment = '';
        this.state.improveComment = '';
        this.state.customer = '';
    }
    

    async onSubmit() {
        if (!this.isFormValid()) {
            this.notification.add("Please fill in all fields before submitting", { type: 'danger' });
            return;
        }

        // Map IDs to names for likes
        const likeNames = this.state.likes.map(id => 
            this.skinAttributes.find(attr => attr.id === id)?.name.toLowerCase()
        );

        // Map IDs to names for improvements
        const improvementNames = this.state.improvements.map(id => 
            this.skinAttributes.find(attr => attr.id === id)?.name.toLowerCase()
        );

        console.log('Customer Name', this.state.customer)

        // Get the names for other fields
        const vascularityName = this.vascularityOptions.find(opt => opt.id === this.state.vascularity)?.name.toLowerCase();
        const skinTextureName = this.skinTextureOptions.find(opt => opt.id === this.state.skinTexture)?.name.toLowerCase();
        const pigmentationName = this.depthOfPigmentationOptions.find(opt => opt.id === this.state.pigmentation)?.name.toLowerCase();
        const hydrationName = this.hydrationLevelOptions.find(opt => opt.id === this.state.hydration)?.name.toLowerCase().replace(' ', '_');
        const sebaceousActivityName = this.sebaceousActivityOptions.find(opt => opt.id === this.state.sebaceousActivity)?.name.toLowerCase();

        // Add likeComment to likeNames if 'Other' is selected
        if (likeNames.includes('other') && this.state.likeComment){
            likeNames[likeNames.indexOf('other')] = this.state.likeComment;
        }

        // Add improveComment to improvementNames if 'Other' is selected
        if (improvementNames.includes('other') && this.state.improveComment){
            improvementNames[improvementNames.indexOf('other')] = this.state.improveComment;
        }

        try {
            const result = await this.orm.create("skin.consultation", [{
                like_about_skin: JSON.stringify(likeNames),
                improve_about_skin: JSON.stringify(improvementNames),
                customer_id: this.state.customerId,
                vascularity: vascularityName,
                vascularity_comment: this.state.vascularityComment,
                skin_texture: skinTextureName,
                skin_texture_comment: this.state.skinTextureComment,
                pigmentation: pigmentationName,
                pigmentation_comment: this.state.pigmentationComment,
                hydration: hydrationName,
                hydration_comment: this.state.hydrationComment,
                sebaceous_activity: sebaceousActivityName,
                sebaceous_activity_comment: this.state.sebaceousActivityComment,
            }]);
            
            this.notification.add("Consultation submitted successfully!", { type: 'success' });


            if (result.length == 1 && result != null){
                this.action.doAction({
                    type: "ir.actions.act_window",
                    res_model: "skin.consultation",
                    res_id: result[0],
                    view_mode: "form",
                    views: [[false, "form"]],
                    target: "current"
                })
                this.emptyFields();
                return result;
            }
        } catch (error) {
            this.notification.add(error, { type: 'danger' });
            this.notification.add("Failed to submit consultation", { type: 'danger' });
        }
    }
}

SkinConsultation.template = 'aloette.SkinConsultation';
registry.category("actions").add("aloette.SkinConsultation", SkinConsultation);
