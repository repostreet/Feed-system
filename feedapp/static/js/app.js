var protocol = 'http://'
var hostname = protocol + window.location.host
var application = angular.module('feedapp', ['ngRoute', 'ngSanitize'])

application.config(function($interpolateProvider, $httpProvider){         
    $interpolateProvider.startSymbol('[[').endSymbol(']]');
});

application.config(['$routeProvider', '$locationProvider', function($routeProvider, $locationProvider){

    // $locationProvider.html5Mode(true);

    $routeProvider
    .when('/', {
        templateUrl: '/static/templates/home.html',
        controller: "homeController"
    })
    .when('/login/', {
        templateUrl: '/static/templates/login.html',
        controller: "loginController"
    })
    .when('/registration/', {
        templateUrl: '/static/templates/registration.html',
        controller: "registrationController"
    })
    .when('/notification/', {
        templateUrl: '/static/templates/notification.html',
        controller: "notificationController"
    })
    .when('/search/:searchText/:searchType/', {
        templateUrl: '/static/templates/search_result.html',
        controller: "searchController"
    })
    .otherwise({
        redirectTo: '/'
    });

}]);

application.controller("homeController", function($scope, $http, $window, $location){
    var authToken = $window.localStorage.getItem('token');
    var url = hostname + /create-article/;
    var live_feed_url = hostname + '/live-feed/'

    console.log(authToken);
    if (authToken == null){
        $location.url('/registration');
    }
    else{
        console.log('Okay');
    }

    $scope.submitArtcileForm = function() {
        var data = $scope.article;

        $http({
            url: url,
            method: "POST",
            data: data,
            headers: {'Authorization': authToken},
        }).then(function(response){
            var fileSelect = document.getElementById('file');
            var files = fileSelect.files;

            var formData = new FormData();
            for (var i = 0; i < files.length; i++) {
                var file = files[i];
                formData.append('file', file, file.name);
            }

            var xhr = new XMLHttpRequest();
            xhr.open('POST', '/upload-file/' + response.data['article_id'] + '/', true);
            xhr.send(formData);
            xhr.onload = function () {
                if (xhr.status === 200) 
                {
                    console.log(xhr.status);
                } 
                else 
                {
                    alert('An error occurred!');
                }
            };
        $scope.hide_article_form = true;
        $scope.form_submitted_message = 'Your status is posted.'

        }).catch(function(error){
            // $scope.error = error.data;
            console.log(error.data);
        });
    }

    // socket connection
    var ws = new WebSocket("ws://localhost:8765/");
    var messages = document.createElement('ul');

    ws.onmessage = function (event) {
        console.log(event.data);
        $scope.live_feed.unshift(JSON.parse(event.data));
        $scope.$apply();
        console.log($scope.live_feed);
    };
    ws.onopen = function(e) {
        console.log("Connected");
    }

    $http({
        url: live_feed_url,
        method: "GET",
        headers: {'Authorization': authToken}
    }).then(function(response){
        var response_data = response.data;
        $scope.live_feed = response_data;
        console.log(response_data);

    }).catch(function(error){
        console.log(error.data);
    });

    $scope.show_comment = function(id) {
       if ($scope['show_comment_list_' + id] == false||$scope['show_comment_list_' + id] == undefined) {
           $scope['show_comment_list_' + id] = true;

       }
       else {
           $scope['show_comment_list_' + id] = false;
       }
    }

    var like_url = hostname + '/like/'
    $scope.likeArticle = function(id) {
        console.log(id);
        var data = {'id': id}
        $http({
            url: like_url,
            method: "POST",
            data: data,
            headers: {'Authorization': authToken}
        }).then(function(response){
            var article_number = 'article_' + id;
            $('#' + article_number).hide();
            $('#' + 'article_' + id + '_liked').text('Wow');
        }).catch(function(error){
            console.log(error.data);
        });
    }

    $scope.showCommentBox = function(id) {
        $scope['show_comment_box_' + id] = true;
        $('#comment_' + id).show();
        $('#hide_comment_box').show();
        $scope.comment_posted_message = null;
    }

    var comment_url = hostname + '/comment/'
    $scope.submitComment = function(id){
        var comment_data = {'comment_body': $('#comment_' + id).val(), 'article_id': id}
        $http({
            url: comment_url,
            method: "POST",
            data: comment_data,
            headers: {'Authorization': authToken}
        }).then(function(response){
            $('#comment_' + id).hide();
            $('#hide_comment_box').hide();
            $scope.comment_posted_message = response.data['message'];
        }).catch(function(error){
            console.log(error.data);
        });
    }

    $scope.searchCtrl = function() {
        var search_title_url = '/search/' + $scope.search_text + '/' + 'title'
        console.log(search_title_url);
        $location.url(search_title_url);
    }

});

application.controller("registrationController", function($scope, $http, $window, $location){
    var url = hostname + '/registration/';
    var headers = {}
    $scope.error = {}

    $scope.submitRegistrationForm = function() {

        if ($scope.user.password1.length < 5 ) {
            $scope.error.password = "Password length should be greater than 5."
        }
        else if ($scope.user.password1 != $scope.user.password2) {
            $scope.error.password = "Password did't match"
        }
        else {
            var data = $scope.user;
            data['password'] = data.password1;

            $http({
                url: url,
                method: "POST",
                data: data,
            }).then(function(response){
                $scope.hide_form = true;
                $scope.form_submitted_message = response.data['message'];

            }).catch(function(error){
                for (var key in error.data) {
                    $scope.error[key] = error.data[key][0];
                }
            });
        }
    }
});

application.controller("loginController", function($scope, $http, $window, $location){
    var url = hostname + '/login/';
    var headers = {}
    $scope.error = {}

    $scope.submitLoginForm = function() {
        var data = $scope.user;
        console.log(data);
        $http({
            url: url,
            method: "POST",
            data: data,
        }).then(function(response){
            $window.localStorage.setItem('token', response.data['Authorization']);
            $location.url('/');
        }).catch(function(error){
            $scope.error = error.data['error'];
        });
    }
});

application.controller("notificationController", function($scope, $http, $window, $location){
    var url = hostname + '/notification/';
    var headers = {}
    $scope.error = {}
    var authToken = $window.localStorage.getItem('token');


    $http({
        url: url,
        method: "GET",
        headers: {'Authorization': authToken}
    }).then(function(response){
        var response_data = response.data;
        $scope.notifications = response_data;
        console.log(response_data);

    }).catch(function(error){
        console.log(error.data);
    });
});

application.controller("searchController", function($scope, $http, $window, $routeParams){
    var url = hostname + '/search/' + $routeParams.searchText + '/' + $routeParams.searchType
    var headers = {}
    $scope.error = {}
    var authToken = $window.localStorage.getItem('token');


    $http({
        url: url,
        method: "GET",
        headers: {'Authorization': authToken}
    }).then(function(response){
        $scope.search_result_list = response.data;
        console.log(response.data);
        console.log('Should work');
    }).catch(function(error){
        console.log(error.data);
    });
});