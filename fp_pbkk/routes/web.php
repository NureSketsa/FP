<?php

use Illuminate\Support\Facades\Route;

Route::get('/', function () {
    return view('main');
});

Route::get('/chat', function () {
    return view('chat');
    });

Route::get('/login', function () {
    return view('login');
    });

Route::get('/register', function () {
    return view('register');
    });

