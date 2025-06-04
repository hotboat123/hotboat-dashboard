from dashboards import crear_app_reservas

if __name__ == '__main__':
    app = crear_app_reservas()
    print("\n=== DASHBOARD DE RESERVAS ===")
    print("Dashboard disponible en: http://localhost:8050")
    print("O alternativamente en: http://127.0.0.1:8050")
    app.run(debug=True, host='localhost', port=8050) 