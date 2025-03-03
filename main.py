if __name__=='__main__':
    try:
        from brain.interface import interface
    except Exception as e:
        print(f"Erro ao iniciar o programa: {e}")
    finally:
        interface()