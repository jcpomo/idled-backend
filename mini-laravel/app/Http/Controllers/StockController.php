<?php
namespace App\Http\Controllers;
use Illuminate\Http\Request;

class StockController extends Controller
{
    private array $stock = [
        'R1' => ['referencia' => 'R1', 'descripcion' => 'Tornillo M3', 'stock' => 42],
        'R2' => ['referencia' => 'R2', 'descripcion' => 'Tuerca M3',   'stock' => 7],
    ];
    public function show(Request $request)
    {
        $ref = $request->query('referencia');
        return response()->json($this->stock[$ref] ?? null);
    }
}
