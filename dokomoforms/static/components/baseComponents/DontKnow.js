var React = require('react'); 

DontKnow = React.createClass({
    render: function() {
        return (
                <div className="question__btn__other">
                    <input type="checkbox" id="dont-know" name="dont-know" value="selected" />
                    <label htmlFor="dont-know">I don't know the answer</label>
                </div>
               )
    }
});

