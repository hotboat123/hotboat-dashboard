from dashboard_marketing import crear_app_marketing

if __name__ == '__main__':
    app = crear_app_marketing()
    print("\n=== DASHBOARD DE MARKETING - META ADS ===")
    print("Dashboard disponible en: http://localhost:8052")
    print("O alternativamente en: http://127.0.0.1:8052")
    app.run(debug=True, host='localhost', port=8052) 