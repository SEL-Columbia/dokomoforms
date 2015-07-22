var React = require('react'); 
var BigButton = require('./baseComponents/BigButton.js');
var DontKnow = require('./baseComponents/DontKnow.js');
var ResponseField = require('./baseComponents/ResponseField.js'); 

/*
 * Footer component
 * Render footer containing a button and possible DontKnow component
 *
 * props:
 *  @showDontKnow: Boolean to activate DontKnow component
 *  @checkBoxFunction: What do on DontKnow component click event
 *  @buttonText: Text to show on big button
 *  @buttonType: Type of big button to render
 *  @showDontKnowBox: Boolean to extend footer and show input field
 */
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

