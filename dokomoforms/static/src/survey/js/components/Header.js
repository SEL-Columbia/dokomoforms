import React from 'react';
import ps from '../../../common/js/pubsub';
import Menu from './baseComponents/Menu.js';

/*
 * Header component
 * Displays the top bar of the Application, includes hambaagah menu
 *
 * props:
 *  @splash: Boolean to render splash header instead of the default
 *  @buttonFunction: What to do on previous button click
 *  @number: Current number to render in header
 *  @db: Active pouch db // XXX rather not pass this to header
 *  @surveyID: active surveyID
 */
export default class Header extends React.Component {

    constructor(props){
        super(props);

        this.onClick = this.onClick.bind(this);

        this.state = {
            showMenu: false
        }
    }

    componentWillMount() {
        const self = this;
        ps.subscribe('settings:language_changed', function() {
            self.setState({
                showMenu: false
            });
        });
    }

    onClick() {
        this.setState({
            showMenu: this.state.showMenu ? false : true
        });
    }

    render() {
        let headerClasses = 'bar bar-nav bar-nav-padded noselect';
        if (this.state.showMenu) {
            headerClasses += ' title-extended';
        }

        return (
            <header className={headerClasses}>
            {this.props.splash ?
                <h1 className='title align-left'>{window.ORGANIZATION}</h1>
             :
                <span>
                <button onClick={this.props.buttonFunction}
                    className='btn btn-link btn-nav pull-left page_nav__prev'>
                    <span className='icon icon-left-nav'></span> <span className=''>Previous</span>
                </button>
                <h1 className='title'>{this.props.number} / {this.props.total}</h1>
                </span>
            }

            <a className='icon icon-bars pull-right menu' onClick = {this.onClick} ></a>

            { this.state.showMenu ?
                <Menu
                    language={this.props.language}
                    survey={this.props.survey}
                    surveyID={this.props.surveyID}
                    db={this.props.db}
                    loggedIn={this.props.loggedIn}
                    hasFacilities={this.props.hasFacilities}
                />
                : null }
            </header>
        );
    }

};
