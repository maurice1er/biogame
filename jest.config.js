// module.exports = {
//   testEnvironment: 'node',
//   reporters: [
//     "default",
//     "jest-html-reporters",
//     "./test-report.html"
//   ]
// };


module.exports = {
  testEnvironment: 'node',
  reporters: [
    "default",
    ["jest-html-reporters", {
      "publicPath": "./",
      "filename": "test-report.html",
      "expand": true
    }]
  ]
};
