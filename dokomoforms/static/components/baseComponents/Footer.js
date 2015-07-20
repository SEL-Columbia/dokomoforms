var React = require('react'); 
var BigButton = require('./BigButton.js');
var DontKnow = require('./DontKnow.js');
var ResponseField = require('./ResponseField.js'); 

module.exports = React.createClass({
    getDontKnow: function() {
        if (this.props.showDontKnow)
            return (<DontKnow 
                        checkBoxFunction={this.props.checkBoxFunction} 
                        questionID={this.props.questionID}
                    />)

        return null;
    },

    render: function() {
        var FooterClasses = "bar bar-standard bar-footer";
        if (this.props.showDontKnow) 
            FooterClasses += " bar-footer-extended";
        if (this.props.showDontKnowBox) 
            FooterClasses += " bar-footer-extended bar-footer-super-extended";

        return (
                <div className={FooterClasses}>
                    <BigButton text={this.props.buttonText} 
                    type={this.props.buttonType}
                    buttonFunction={this.props.buttonFunction} />
                    { this.getDontKnow() }
                    { this.props.showDontKnowBox ? <ResponseField /> : null}
                </div>
               )
    }
});

