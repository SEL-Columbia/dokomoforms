<div class="modal fade modal-user" tabindex="-1" role="dialog" aria-labelledby="<%= data.id ? 'Edit' : 'Add' %> User" aria-hidden="true">
    <div class="modal-dialog modal-lg">
        <div class="modal-content">
            <form>
                <div class="modal-header">
                    <button type="button" class="close" data-dismiss="modal" aria-label="Close"><span aria-hidden="true">&times;</span></button>
                    <h4 class="modal-title"><%= data.id ? 'Edit' : 'Add' %> User</h4>
                </div>
                <div class="modal-body">
                        <div class="form-group">
                            <label for="user-name">Name</label>
                            <input type="text" class="form-control" id="user-name" placeholder="Name" value="<%= data.name %>">
                        </div>
                        <div class="form-group">
                            <label for="user-email">Email</label>
                            <input type="email" class="form-control" id="user-email" placeholder="Email" value="<%= data.emails ? data.emails[0] : '' %>">
                        </div>
                        <div class="form-group">
                            <label for="user-role">Role</label>
                            <select class="form-control" id="user-role"
                            <%= data.id ? 'disabled' : '' %>
                            >
                                <option <%= (data.role === 'enumerator') ? "selected" : "" %>>enumerator</option>
                                <option <%= (data.role === 'administrator') ? "selected" : "" %>>administrator</option>
                            </select>
                        </div>
                        <div class="form-group">
                            <label for="user-default-lang">Default Language</label>
                            <select class="form-control" id="user-default-lang">
                                <option <%= (data.preferences && data.preferences.default_language === 'English') ? "selected" : "" %>>English</option>
                                <option <%= (data.preferences && data.preferences.default_language === 'Español') ? "selected" : "" %>>Español</option>
                            </select>
                        </div>

                        <!-- Surveys for enumerators -->
                        <div class="form-group">
                            <% if (data.role === 'enumerator') { %>
                            <label for="user-surveys">Allowed Surveys
                                <span class="info-icon" data-toggle="tooltip" data-placement="right" title="" data-original-title="This enumerator will only be allowed to submit to the surveys selected here.">i</span>
                            </label>
                            <select multiple class="form-control" id="user-surveys">
                                <% data.all_surveys.forEach(function(survey) { %>
                                    <% if (survey.survey_type === 'enumerator_only') { %>
                                        <option
                                            value="<%= survey.id %>"
                                            <% if (data.allowed_surveys.indexOf(survey.id) !== -1) { %>
                                                selected
                                            <% } %>
                                        >
                                            <%= data._t(survey.title) %>
                                        </option>
                                    <% } %>
                                <% }); %>
                            </select>
                            <% } else if(data.role === 'administrator') { %>
                            <label for="user-surveys">Admin Surveys
                                <span class="info-icon" data-toggle="tooltip" data-placement="right" title="" data-original-title="This user will be able to administer the surveys selected here.">i</span>
                            </label>
                            <select multiple class="form-control" id="user-surveys">
                                <% data.all_surveys.forEach(function(survey) { %>
                                    <option
                                        value="<%= survey.id %>"
                                        <% if (data.admin_surveys && data.admin_surveys.indexOf(survey.id) !== -1) { %>
                                            selected
                                        <% } %>
                                    >
                                        <%= data._t(survey.title) %>
                                    </option>
                                <% }); %>
                            </select>
                            <% } %>
                        </div>
                </div>
                <div class="modal-footer">
                    <% if (data.id) { %>
                        <button type="button" class="btn btn-danger btn-delete-user pull-left">Delete User</button>
                    <% } %>
                    <button type="button" class="btn btn-default" data-dismiss="modal">Cancel</button>
                    <button type="button" class="btn btn-primary btn-save-user">Save</button>
                </div>
            </form>
        </div>
    </div>
</div>
