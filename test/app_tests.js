var jsdom = require('jsdom');
var should = require('should');

// Creating the app and loading up survey questions
describe('App initalization Tests', function(done) {
    // globals
    var window;
    var raw_survey;

    before(function(done) {
        done();
    });

    beforeEach(function(done) {
        raw_survey = require('./fixtures/survey.json');
        jsdom.env('./test/widgets.html',  
            ['lib/classList_shim.js',
            '../static/lib.js',  
            '../static/app.js'], 
            function(error, win) {
                if (error) { 
                    console.log(error);
                    throw (error) 
                };
            
                window = win;
                window.localStorage = {};
                done();
            });

    });

    afterEach(function(done) {
        raw_survey = null;
        window.close();
        window = null;
        done();
    });

    it('should init app and survey juust fine', 
        function(done) {
            window.App.init(raw_survey);
            raw_survey.metadata.location.should.match(window.App.start_loc);
            should(window.App.survey).be.ok;

            var survey = window.App.survey;
            should(survey.id).match(raw_survey.survey_id);
            should(survey.questions).match(raw_survey.questions);
            should(survey.metadata).match(raw_survey.metadata);
            done();
        });

    it('should order the survey questions just fine', 
        function(done) {
            window.App.init(raw_survey);
            var survey = window.App.survey;
            
            var question = survey.current_question;
            var sequence_num = 1;

            var len = survey.questions.length;

            while(question) {
                sequence_num.should.match(question.sequence_number);
                sequence_num++;
                question = question.next;
            }

            sequence_num.should.match(len + 1);
            done();
        });
    
    it('should fill in submitter name', 
        function(done) {
            var name = 'viktor sucks';
            window.localStorage['name'] = name;
            window.App.init(raw_survey);
            window.App.submitter_name.should.match(name);
            done();
        });

    it('should load previous submission values',
            //XXX:maybe it shouldn't?
        function(done) {
            answers = {
                "22a915d2-19cd-4de3-8225-aaecc7a90c1b":[123,null,123123],
                "6a4036b4-881b-4838-8cf6-4948cb113077":[[-73.965,40.80]],
                "7cf402f6-841b-41fb-a585-1c4af49e570c":[null,null,"ewrwrwr"],
            }
            window.localStorage["fc76fe08-9a6c-43cf-b30f-4b9b4ee97af2"] = 
               JSON.stringify(answers); 
            
            window.App.init(raw_survey);

            var response = window.App.survey.questions[0].answer[0];
            response.should.match(123);
            response = window.App.survey.questions[0].answer[2];
            response.should.match(123123);
            response = window.App.survey.questions[2].answer[0][0];
            response.should.match(-73.965);
            response = window.App.survey.questions[7].answer[2];
            response.should.match("ewrwrwr");

            done();
        });
    
});


