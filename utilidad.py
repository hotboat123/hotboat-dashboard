from dashboards import crear_app_utilidad

if __name__ == '__main__':
    app = crear_app_utilidad()
    print("Dashboard de UTILIDAD OPERATIVA disponible en: http://localhost:8051")
    print("O alternativamente en: http://127.0.0.1:8051")
    app.run(debug=True, host='localhost', port=8051) 