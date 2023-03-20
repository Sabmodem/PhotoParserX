const gulp = require('gulp');
const geb = require('gulp-esbuild');
// const ev = require('esbuild-vue');
const ev = require('esbuild-plugin-vue3');

const src_task = () => {
  return gulp.src('./src/main.js')
    .pipe(geb({
      outfile: 'main.js',
      bundle: true,
      plugins: [ev()],
      loader: {
        '.tsx': 'jsx',
        ".woff": 'dataurl',
        ".woff2": 'dataurl'
      },
    }))
    .pipe(gulp.dest(`${__dirname}/static/build`));
};

const watch_task = () => {
  gulp.series(src_task)();

  const src_dir = `${__dirname}/src`;
  const watch_vue = `${src_dir}/*.vue`;
  const watch_js = `${src_dir}/*.js`;
  gulp.watch([
    watch_vue, 
    watch_js,
    `${src_dir}/views/*.vue`,
    `${src_dir}/assets/*.css`,
    `${src_dir}/components/*.vue`
  ], gulp.series(src_task));
};

exports.src = watch_task;
