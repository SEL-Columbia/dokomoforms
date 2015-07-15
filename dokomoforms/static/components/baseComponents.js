var React = require('react');
ResponseField = React.createClass({
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

Message = React.createClass({
    render: function() {
        var textClass = this.props.classes;
        return (
                <div className='content-padded'>
                        <p className={textClass}>{this.props.text}</p>
                </div>
               )
    }
});

ResponseFields = React.createClass({
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

Title = React.createClass({
    render: function() {
        return ( 
                <div className="content-padded">
                    <h3>test_survey</h3>
                    <p>version 1 | last updated Thu Jul 02 2015</p>
                </div>
               )
    }
});

BigButton = React.createClass({
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

LittleButton = React.createClass({
    render: function() {
        var iconClass = "icon " + this.props.icon;
        return (
                <div className="content-padded">
                    <button className="btn">
                        {this.props.icon ? <span className={iconClass}></span> : null }
                        {this.props.text}
                    </button>
                </div>
               )
    }
});

Select = React.createClass({
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
       var size = this.props.multiSelect ? 
           this.props.choices.length + 1 + 1*this.props.withOther : 1;
        return (
                <div className="content-padded">
                    <select className="noselect" onChange={this.onChange} 
                            multiple={this.props.multiSelect}
                            size={size}
                    >

                    <option key="null" value="null">Please choose an option</option>
                    {this.props.choices.map(function(choice) {
                        return (
                                <option key={choice.value} value={choice.value}>
                                    { choice.text }
                                </option>
                                )
                    })}
                    {this.props.withOther ? 
                        <option key="other" value="other"> Other </option> 
                        : null}
                    </select>
                    {this.state.showOther ? <ResponseField />: null}
                </div>
               )

    }
});

FacilityRadios = React.createClass({
    render: function() {
        return (
                <div className='question__radios'>
                {this.props.facilities.map(function(facility) {
                    return (<div key={facility.value} className='question__radio'>
                            <input 
                                type='radio' 
                                id={facility.value} 
                                name='facility' 
                                value={facility.value}> 
                            </input>
                            <label htmlFor={facility.value} >
                            <span className="question__radio__span__btn"><span></span></span>
                                <strong>{facility.name}</strong>
                            </label>
                            <br/>
                            <span className='question__radio__span__meta'>
                                {facility.sector}
                            </span>
                            <span className='question__radio__span__meta'>
                                <em>{facility.distance}m</em>
                            </span>
                            </div>) 
                })}
                </div>
               )
    }
});

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

Footer = React.createClass({
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

Question = React.createClass({
    render: function() {
        return (
                <ResponseFields childCount={3} />
               )
    }
});

Menu = React.createClass({
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

Card = React.createClass({
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
                            <span> {msg} <br/> </span> 
                        )
                })}
                </div>
            </div>
       )
    }
});

Header = React.createClass({
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
            {this.props.splash ?
                <h1 className="title align-left">independant</h1>
             :   
                <span>
                <button className="btn btn-link btn-nav pull-left page_nav__prev">
                    <span className="icon icon-left-nav"></span> <span className="">Previous</span>
                </button>
                <h1 className="title">7 / 11</h1>
                </span>
            }

            <a className="icon icon-bars pull-right menu" onClick = {this.onClick} ></a>

            { this.state.showMenu ? <Menu /> : null }
            </header>
        )
    }

});

