var React = require('react');

var ResponseField = React.createClass({
    render: function() {
        return (
                <div className="input_container">
                    <input 
                        type={this.props.type ? this.props.type : "text"} 
                        placeholder="Please provide a response." 
                        value=""
                     >
                     {this.props.showMinus ? 
                        <span className="icon icon-close question__minus"></span>
                        : null}
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
                    return <ResponseField key={idx + 1} showMinus={true}/>;
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

var Select = React.createClass({
    getInitialState: function() {
        return { showOther: false }
    },

    onChange: function(e) {
        var foundOther = false;
        for (var i = 0; i < e.target.selectedOptions.length; i++) {
            option = e.target.selectedOptions[i]; 
            foundOther = foundOther | option.value === "other";
        }

        this.setState({showOther: foundOther})
    },

    render: function() {
        return (
                <div>
                <select className="noselect"
                    onChange={this.onChange} >

                <option value="null">Please choose an option</option>
                <option value="1f77897b-7b10-4277-80da-8bc29084b025">choice a</option>
                <option value="-7b10-4277-80da-8bc29084b025">choice b</option>
                {this.props.withOther ? 
                    <option value="other"> Other </option> 
                    : null}
                </select>
                {this.state.showOther ? <ResponseField />: null}
                </div>
               )

    }
});


var DontKnow = React.createClass({
    render: function() {
        return (
                <div className="question__btn__other">
                    <input type="checkbox" id="dont-know" name="dont-know" value="selected" />
                    <label htmlFor="dont-know">I don't know the answer</label>
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
                            <span key={msg}> 
                                {msg}
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
                    <div className={contentClasses}>
                        <Title />
                        <Card messages={["hey", "how you doing", 
                            ["i ", <b>love</b>, " toast"]]} type={"message-error"}/>
                        <Card messages={["cool"]} />
                        <BigButton text={'Click for toast'} type={'btn-positive'} />
                        <Question />
                        <LittleButton text={'add another answer'} />
                        <Select withOther={true}/>
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
