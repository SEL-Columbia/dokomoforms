var React = require('react');

var ResponseField = React.createClass({
    render: function() {
        return (
                <div className="input_container">
                    <input 
                        type="text" 
                        placeholder="Please provide a response." 
                        value=""
                     >
                        <span className="icon icon-close question__minus"></span>
                    </input>
                 </div>
               )
    }
});

var ResponseFields = React.createClass({
    render: function() {
        var children = Array.apply(null, {length: this.props.childCount})
        return (
                <div>
                {children.map(function(child, idx) {
                    return <ResponseField key={idx + 1} />;
                })}
                </div>
               )
    }
});

var Title = React.createClass({
    render: function() {
        return ( 
                <div className="content-padded">
                    <h3>test_survey</h3>
                    <p>version 1 | last updated Thu Jul 02 2015</p>
                </div>
               )
    }
});

var BigButton = React.createClass({
    render: function() {
        var buttonClasses = "btn btn-block navigate-right page_nav__next";
        if (this.props.type) {
            buttonClasses += " " + this.props.type;
        } else {
            buttonClasses += " btn-primary";
        }

        return (
                <div className="bar-padded">
                <button className={buttonClasses}>
                {this.props.text}
                </button>
                </div>
               )
    }
});

var LittleButton = React.createClass({
    render: function() {
        return (
                <div className="content-padded">
                    <button className="btn">
                        {this.props.text}
                    </button>
                </div>
               )
    }
});

var DontKnow = React.createClass({
    render: function() {
        return (
                <div className="question__btn__other">
                    <input type="checkbox" id="dont-know" name="dont-know" value="selected" />
                    <label for="dont-know">I don't know the answer</label>
                </div>
               )
    }
});

var Footer = React.createClass({
    render: function() {
        var FooterClasses = "bar bar-standard bar-footer";
        if (this.props.showDontKnow) 
            FooterClasses += " bar-footer-extended";
        return (
                <div className={FooterClasses}>
                    <BigButton text={'Next Question'} />
                    { this.props.showDontKnow ? <DontKnow /> : null }
                </div>
               )
    }
});

var Question = React.createClass({
    render: function() {
        return (
                <ResponseFields childCount={3} />
               )
    }
});

var Menu = React.createClass({
    render: function() {
        return (
            <div className="title_menu">
                <div className="title_menu_option menu_restart">
                    Cancel survey
                </div>
                <div className="title_menu_option menu_save">
                    Save current state and exit
                </div>
                <div className="title_menu_option menu_clear">
                    Clear all saved surveys
                </div>
            </div>
       )
    }
});

var Card = React.createClass({
    getInitialState: function() {
        return { 
            isBold : function(str) {
                var bold = /<b>.*?<\/b>/g;
                return bold.test(str);
            },

            getBoldStr : function(str) {
                var bold = /(.*?)<b>(.*?)<\/b>/g;
                return str.replace(bold, "$1");
            }
        }
    },
    render: function() {
        var messageClass = "message-box";
        if (this.props.type) { 
            messageClass += " " + this.props.type;
        } else {
            messageClass += " message-primary";
        }

        var self = this;
        return (
            <div className="content-padded">
                <div className={messageClass} >
                {this.props.messages.map(function(msg, idx) {
                    return ( 
                            <span key={idx + 1}> 
                                {
                                    function() {
                                        if (self.state.isBold(msg)) {
                                           return ( 
                                                   <strong>
                                                    {self.state.getBoldStr(msg)}
                                                   </strong>
                                                  )
                                        } else {
                                            return msg
                                        }
                                    }()
                                }
                                <br />
                            </span> 
                        )
                })}
                </div>
            </div>
       )
    }
});

var Header = React.createClass({
    getInitialState: function() {
        return { showMenu: false }
    },
    onClick: function() {
        this.setState({showMenu: this.state.showMenu ? false : true })
    },
    render: function() {
        var headerClasses = "bar bar-nav bar-padded noselect";
        if (this.state.showMenu) 
            headerClasses += " title-extended";

        return (
            <header className={headerClasses}>
            <h1 className="title align-left">independant</h1>
            <a className="icon icon-bars pull-right menu"
                onClick = {this.onClick}
            ></a>
            { this.state.showMenu ? <Menu /> : null }
            </header>
        )
    }

});

var Application = React.createClass({
    getInitialState: function() {
        return { showDontKnow: true }
    },
    render: function() {
        var contentClasses = "content";
        if (this.state.showDontKnow) 
            contentClasses += " content-shrunk";

        return (
                <div id="wrapper">
                    <Header />
                    <div className="content">
                        <Title />
                        <Card messages={["hey", "how you doing", "i <b>love</b> toast"]} type={"message-error"}/>
                        <Card messages={["cool"]} />
                        <BigButton text={'Click for toast'} type={'btn-positive'} />
                        <Question />
                    </div>
                    <Footer showDontKnow={this.state.showDontKnow}/>
                </div>
               )
    }
});

var ApplicationData = {};
init = function(survey) {
    ApplicationData.survey = survey;
    React.render(
            <Application />,
            document.body
    );
};
