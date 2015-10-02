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
                        <label for="user-default-lang">Default Language</label>
                        <select class="form-control" id="user-default-lang">
                            <option <%= (data.preferences && data.preferences.default_language === 'English') ? "selected" : "" %>>English</option>
                            <option <%= (data.preferences && data.preferences.default_language === 'Español') ? "selected" : "" %>>Español</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label for="user-api-token">API Token</label>
                        <p class="help-block">Generating a new token will invalidate the existing token.</p>
                        <div class="input-group">
                            <span class="input-group-btn">
                                <button type="button" class="btn btn-default btn-api-key"><span class="glyphicon glyphicon-refresh"></span> Generate Token </button>
                            </span>
                            <input type="text" class="form-control" id="user-api-token" placeholder="API Token">
                        </div>
                    </div>
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-default" data-dismiss="modal">Cancel</button>
                    <button type="button" class="btn btn-primary btn-save-user">Save</button>
                </div>
            </form>
        </div>
    </div>
</div>
