var React = require('react'); 
module.exports = React.createClass({
    render: function() {
        return (
                <div className="question__btn__other">
                    <input 
                        onClick={this.props.checkBoxFunction}
                        type="checkbox" 
                        id="dont-know" 
                        name="dont-know" 
                        value="selected" 
                        key={this.props.questionID}
                    />
                    <label htmlFor="dont-know">I don't know the answer</label>
                </div>
               )
    }
});

