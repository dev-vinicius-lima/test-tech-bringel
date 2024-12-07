from sqlalchemy.orm import Session
from app.models import Step, Material, Serial, Failure

def initialize_steps(session: Session):
    steps = [
        {"process_name": "Recebimento", "description": "Etapa de recebimento dos materiais dos diversos setores do hospital"},
        {"process_name": "Lavagem", "description": "Etapa onde é feita uma lavagem dos materiais"},
        {"process_name": "Esterilização", "description": "Etapa onde os materiais cirúrgicos são esterilizados com alta temperatura"},
        {"process_name": "Distribuição", "description": "Etapa onde é feito a distribuição dos materiais cirúrgicos para os diversos setores do Hospital"},
    ]
    
    # for step in steps:
    #     existing_step = session.query(Step).filter(Step.process_name == step['process_name']).first()
    #     if not existing_step:
    #         session.add(Step(**step))
    #         print(f"Adicionando etapa: {step['process_name']}")
    
    session.commit()
    # print("Todas as etapas foram adicionadas ou já existiam.")

def create_material(session: Session, name: str, material_type: str, expiration_date: str, serial: str, current_step_id: int):
    # Ensure the step exists before creating a material
    step = session.query(Step).filter(Step.id == current_step_id).first()
    if not step:
        print(f"Erro: A etapa com ID {current_step_id} não existe.")
        return

    new_material = Material(
        name=name,
        material_type=material_type,
        expiration_date=expiration_date,
        serial=serial,
        current_step_id=current_step_id
    )
    session.add(new_material)
    session.commit()
    print(f"Material '{name}' criado com sucesso.")

# Example usage
if __name__ == "__main__":
    from app.database import SessionLocal

    # Create a new session
    session = SessionLocal()

    # Initialize steps
    initialize_steps(session)

    # Create a new material (example)
    create_material(session, "Material A", "Tipo A", "2024-12-31", "123456", 1)  # Assuming step ID 1 exists

    # Close the session
    session.close()