<?php
use Illuminate\Support\Facades\Route;
use App\Http\Controllers\AuthController;
use App\Http\Controllers\FacturaController;
use App\Http\Controllers\StockController;

Route::post('/login', [AuthController::class, 'login']);
Route::get('/facturas', [FacturaController::class, 'index']);
Route::get('/stock', [StockController::class, 'show']);
