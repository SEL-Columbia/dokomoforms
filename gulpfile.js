var gulp = require('gulp'),
    uglify = require('gulp-uglify'),
    htmlreplace = require('gulp-html-replace'),
    source = require('vinyl-source-stream'),
    buffer = require('vinyl-buffer'),
    concat = require('gulp-concat'),
    order = require('gulp-order'),
    browserify = require('browserify'),
    watchify = require('watchify'),
    reactify = require('reactify'),
    streamify = require('gulp-streamify'),
    underscorify = require("node-underscorify"),
    less = require('gulp-less'),
    sourcemaps = require('gulp-sourcemaps'),
    replace = require('gulp-replace'),
    livereload = require('gulp-livereload');

// base paths
var static_path = 'dokomoforms/static',
    bower_path = static_path + '/src/bower',
    template_path = 'dokomoforms/templates';

// explicit file/dir paths
var path = {
    HTML: template_path + '/index.html',

    // All less src files, for watch task
    LESS_SRC: [
        static_path + '/src/less/*.less',
        static_path + '/src/bootstrap/less/*.less'
    ],

    // SURVEY CSS
    LESS_ENTRY_POINT: static_path + '/src/less/survey.less',
    RATCHET_CSS: static_path + '/src/ratchet-2.0.2/dist/css/ratchet.css',
    CSS_DIST: static_path + '/dist/css/survey',
    CSS_BUILD: static_path + '/dist/css/survey/*.css',


    ADMIN_LESS_ENTRY_POINT: static_path + '/src/less/admin.less',
    ADMIN_BOOTSTRAP_LESS_ENTRY_POINT: static_path + '/src/bootstrap/less/bootstrap.less',
    ADMIN_CSS_EXTRAS_SRC: [
        static_path + '/src/less/dataTables.bootstrap.css'
    ],
    ADMIN_CSS_DIST: static_path + '/dist/css/admin',
    ADMIN_CSS_BUILD: static_path + '/dist/css/admin/*.css',

    // SURVEY JAVASCRIPT
    JS_LIBS_SRC: [
        bower_path + '/jquery/dist/jquery.js',
        bower_path + '/bootstrap/dist/js/bootstrap.js',
        bower_path + '/lodash/lodash.js',
        bower_path + '/react/react.js'
    ],
    JS_APP_SRC: static_path + '/src/js',
    JS_DIST: static_path + '/dist/js',
    JS_BUILD_FILENAME: 'build.js',
    JS_MINIFIED_BUILD_FILENAME: 'build.min.js',
    JS_DEST_BUILD: static_path + '/dist/js',
    JS_ENTRY_POINT: static_path + '/src/js/main.js',

    // IMAGES
    IMG_SRC: static_path + '/src/img/**/*',
    IMG_DIST: static_path + '/dist/img',

    // FONTS
    FONT_SRC: [
        static_path + '/src/bootstrap/fonts/*',
        static_path + '/src/ratchet-2.0.2/fonts/*',
        static_path + '/src/fonts/*'
    ],
    FONT_DIST: static_path + '/dist/fonts',

    // APP CACHE
    APP_CACHE_SRC: static_path + '/src/cache.appcache',
    APP_CACHE_DIST: static_path + '/dist'
};

//
// DEV TASKS
//

process.env.BROWSERIFYSHIM_DIAGNOSTICS=1;

// Currently unused. Copies the html to the dist destination.
gulp.task('copy', function() {
    gulp.src(path.HTML)
        .pipe(gulp.dest(path.DEST));
});

gulp.task('app-cache', function() {
    gulp.src(path.APP_CACHE_SRC)
        .pipe(replace(/\$date/g, Date.now()))
        .pipe(gulp.dest(path.APP_CACHE_DIST));
});

// Concat all Vendor dependencies
gulp.task('libs', function() {
    gulp.src( path.JS_LIBS_SRC )
       .pipe(concat('libs.js'))
       .pipe(gulp.dest(path.JS_DIST));
});

// Custom LESS compiling
gulp.task('less', function() {
    // survey
    gulp.src(path.LESS_ENTRY_POINT)
        .pipe(less())
        // handle errors so the compiler doesn't stop
        .on('error', function (err) {
            console.log(err.message);
            this.emit('end');
        })
        .pipe(gulp.dest(path.CSS_DIST));

    // admin
    gulp.src(path.ADMIN_LESS_ENTRY_POINT)
        .pipe(less())
        // handle errors so the compiler doesn't stop
        .on('error', function (err) {
            console.log(err.message);
            this.emit('end');
        })
        .pipe(gulp.dest(path.ADMIN_CSS_DIST));
});

// Bootstrap LESS compiling
gulp.task('bootstrap', function() {
    // admin
    return gulp.src(path.ADMIN_BOOTSTRAP_LESS_ENTRY_POINT)
        .pipe(less())
        // handle errors so the compiler doesn't stop
        .on('error', function (err) {
            console.log(err.message);
            this.emit('end');
        })
        .pipe(gulp.dest(path.ADMIN_CSS_DIST));
});

// Compile both custom and bootstrap LESS, then concat into a single
// CSS output.
gulp.task('css', ['less', 'bootstrap'], function() {
    // survey
    gulp.src([path.RATCHET_CSS, path.CSS_DIST + '/*.css', '!' + path.CSS_DIST + '/all-styles.css'])
        .pipe(concat('all-styles.css'))
        .pipe(gulp.dest(path.CSS_DIST))
        .on('error', function (err) {
            console.log(err.message);
            this.emit('end');
        })
        .pipe(livereload());

    // admin
    gulp.src([path.ADMIN_CSS_DIST + '/*.css', '!' + path.ADMIN_CSS_DIST + '/all-styles.css'])
        .pipe(concat('all-styles.css'))
        .pipe(gulp.dest(path.ADMIN_CSS_DIST))
        .on('error', function (err) {
                console.log(err.message);
                this.emit('end');
            })
        .pipe(livereload());
});

// Move images to dist directory
gulp.task('img', function() {
    gulp.src(path.IMG_SRC)
        .pipe(gulp.dest(path.IMG_DIST));
});

// Move fonts to dist directory
gulp.task('fonts', function() {
    gulp.src(path.FONT_SRC)
        .pipe(gulp.dest(path.FONT_DIST));
});


// Watch for changes to ann of the less files or javascript files
// and recompile to dist
gulp.task('watch', ['css', 'img', 'fonts'], function() {
    livereload.listen();
    gulp.watch([path.LESS_SRC, path.APP_CACHE_SRC], ['css', 'img', 'fonts', 'app-cache']);

    var watcher = watchify(browserify({
        entries: [path.JS_ENTRY_POINT],
        transform: [reactify, underscorify],
        debug: true,
        cache: {},
        packageCache: {},
        fullPaths: false
    }));

    return watcher.on('update', function() {
            watcher.bundle()
                .on('error', function (err) {
                    console.log(err.message);
                    this.emit('end');
                })
                .pipe(source(path.JS_BUILD_FILENAME))
                .pipe(buffer())
                .pipe(sourcemaps.init({loadMaps: true})) // loads map from browserify file
                // Add transformation tasks to the pipeline here.
                .pipe(sourcemaps.write('./')) // writes .map file
                .pipe(gulp.dest(path.JS_DIST));

            console.log('Updated');

        })
        .bundle()
        .on('error', function (err) {
            console.log(err.message);
            this.emit('end');
        })
        .pipe(source(path.JS_BUILD_FILENAME))
        .pipe(buffer())
        .pipe(sourcemaps.init({loadMaps: true})) // loads map from browserify file
                // Add transformation tasks to the pipeline here.
                .pipe(sourcemaps.write('./')) // writes .map file
        .pipe(gulp.dest(path.JS_DIST));
});

//
// PROD TASKS
//

gulp.task('build', function() {
    browserify({
            entries: [path.JS_ENTRY_POINT],
            transform: [reactify]
        })
        .bundle()
        .pipe(source(path.JS_MINIFIED_BUILD_FILENAME))
        .pipe(streamify(uglify(path.JS_MINIFIED_BUILD_FILENAME)))
        .pipe(gulp.dest(path.JS_DEST_BUILD));
});

gulp.task('default', ['libs', 'css', 'app-cache', 'watch']);