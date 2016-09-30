<div class="modal fade modal-user" tabindex="-1" role="dialog" aria-labelledby="Settings" aria-hidden="true">
    <div class="modal-dialog modal-lg">
        <div class="modal-content">
            <form>
                <div class="modal-header">
                    <button type="button" class="close" data-dismiss="modal" aria-label="Close"><span aria-hidden="true">&times;</span></button>
                    <h4 class="modal-title">Settings</h4>
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
                        <label for="user-ui-lang">Admin User Interface Language</label>
                        <select class="form-control" id="user-ui-lang">
                            <option <%= (data.preferences && data.preferences.ui_language === 'English') ? "selected" : "" %>>English</option>
                            <option <%= (data.preferences && data.preferences.ui_language === 'Español') ? "selected" : "" %> value="Español">Español (not yet available)</option>
                            <option <%= (data.preferences && data.preferences.ui_language === 'French') ? "selected" : "" %> value="French">French (not yet available)</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label for="user-preferred-lang">Preferred Survey Language</label>
                        <span class="help-block">If available, this language will be used as a default to display a Survey's translatable fields. If not available, the default language for the Survey will be used. <strong>Note that a display language can be set for each individual Survey, overriding this default preference.</strong></span>
                        <select class="form-control" id="user-preferred-lang">
                            <option <%= (data.preferences && data.preferences.default_language === 'English') ? "selected" : "" %>>English</option>
                            <option <%= (data.preferences && data.preferences.default_language === 'Español') ? "selected" : "" %> value="Español">Español (not yet available)</option>
                            <option <%= (data.preferences && data.preferences.default_language === 'French') ? "selected" : "" %> value="French">French (not yet available)</option>
                        </select>
                    </div>
                <% if (data.role === 'administrator') { %>
                    <div class="form-group">
                        <label for="user-api-token">API Token</label>
                        <p class="help-block">Generating a new token will invalidate the existing token.</p>
                        <div class="input-group">
                            <span class="input-group-btn">
                                <button type="button" class="btn btn-secondary btn-api-key"><span class="glyphicon glyphicon-refresh icon-inline-left"></span> Generate Token </button>
                            </span>
                            <input type="text" class="form-control" id="user-api-token" placeholder="API Token">
                        </div>
                        <div class="alert alert-warning alert-token-expiration hide">
                            <span class="glyphicon glyphicon-exclamation-sign icon-inline-left"></span>
                            <span class="token-expiration-text"></span>
                        </div>
                    </div>
                <% } %>
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-default" data-dismiss="modal">Cancel</button>
                    <button type="button" class="btn btn-primary btn-save-user">Save</button>
                </div>
            </form>
        </div>
    </div>
</div>
