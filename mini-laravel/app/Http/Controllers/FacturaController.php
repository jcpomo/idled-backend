<?php
namespace App\Http\Controllers;

use Illuminate\Http\Request;

class FacturaController extends Controller
{
    private array $facturas = [
        ['id' => 'F-1001', 'cliente' => 'ACME',   'total' => 1200.50, 'vencimiento' => '2026-07-15', 'pagada' => false],
        ['id' => 'F-1002', 'cliente' => 'Globex', 'total' => 340.00,  'vencimiento' => '2026-06-20', 'pagada' => true],
        ['id' => 'F-1003', 'cliente' => 'Initech','total' => 980.75,  'vencimiento' => '2026-07-30', 'pagada' => false],
    ];

    public function index(Request $request)
    {
        $data = $this->facturas;
        if ($request->has('pagada')) {
            $pagada = $request->query('pagada') === '1';
            $data = array_values(array_filter($data, fn ($f) => $f['pagada'] === $pagada));
        }
        return response()->json($data);
    }
}
