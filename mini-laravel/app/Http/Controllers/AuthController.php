<?php
namespace App\Http\Controllers;

use Firebase\JWT\JWT;
use Illuminate\Http\Request;

class AuthController extends Controller
{
    // Seed "users": email => [role, name]
    private array $users = [
        'ana@idled.test'  => ['role' => 'administracion', 'name' => 'Ana Admin'],
        'leo@idled.test'  => ['role' => 'comercial',      'name' => 'Leo Comercial'],
        'pro@idled.test'  => ['role' => 'produccion',     'name' => 'Pro Duccion'],
    ];

    public function login(Request $request)
    {
        $email = $request->input('email');
        if (!isset($this->users[$email])) {
            return response()->json(['error' => 'invalid credentials'], 401);
        }
        $u = $this->users[$email];
        $payload = [
            'sub'  => $email,
            'role' => $u['role'],
            'name' => $u['name'],
            'iat'  => time(),
            'exp'  => time() + 3600,
        ];
        $token = JWT::encode($payload, env('JWT_SECRET'), 'HS256');
        return response()->json(['token' => $token]);
    }
}
