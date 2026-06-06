import os
from sqlalchemy.orm import Session
import hashlib
import secrets
from backend.app.database import engine, Base
from backend.app.models import Tenant, User, QuestionnaireItem
from backend.app.seed_big_five_ipip import construir_itens_bigfive

def seed_db(db: Session):
    # 1. Cria tabelas se não existirem
    Base.metadata.create_all(bind=engine)
    
    # 2. Cria Tenant de teste se não houver
    tenant = db.query(Tenant).filter(Tenant.name == "Empresa Demonstração LTDA").first()
    if not tenant:
        tenant = Tenant(name="Empresa Demonstração LTDA")
        db.add(tenant)
        db.commit()
        db.refresh(tenant)
        print("Tenant criado.")

    # 3. Cria Usuários de Teste se não houver
    users_data = [
        {"email": "admin@empresa.com", "name": "Administrador do RH", "role": "hr", "tenant_id": tenant.id},
        {"email": "candidato@empresa.com", "name": "José da Silva (Candidato)", "role": "respondent", "tenant_id": tenant.id},
        {"email": "super@sistema.com", "name": "Super Admin Global", "role": "admin", "tenant_id": None}
    ]
    
    for u_data in users_data:
        user = db.query(User).filter(User.email == u_data["email"]).first()
        if not user:
            salt = secrets.token_hex(16)
            dk = hashlib.pbkdf2_hmac("sha256", "123456".encode("utf-8"), salt.encode("utf-8"), 100000)
            hashed_pwd = f"pbkdf2_sha256$100000${salt}${dk.hex()}"
            user = User(
                email=u_data["email"],
                hashed_password=hashed_pwd,
                full_name=u_data["name"],
                role=u_data["role"],
                tenant_id=u_data["tenant_id"]
            )
            db.add(user)
            db.commit()
            print(f"Usuário {u_data['email']} criado com senha '123456'.")

    # 4. Verifica se já existem itens cadastrados
    count_items = db.query(QuestionnaireItem).count()
    should_seed_base_items = count_items == 0
    if not should_seed_base_items:
        print(f"Itens do questionário já cadastrados ({count_items} itens). Pulando seed DISC/Spranger/Jung.")

    # 5. Seed de Itens do DISC (24 Blocos de 4 Adjetivos)
    disc_blocks = [
        # Bloco 1
        {"D": "Audacioso", "I": "Persuasivo", "S": "Paciente", "C": "Preciso"},
        # Bloco 2
        {"D": "Decisivo", "I": "Entusiasta", "S": "Calmo", "C": "Meticuloso"},
        # Bloco 3
        {"D": "Assertivo", "I": "Sociável", "S": "Estável", "C": "Analítico"},
        # Bloco 4
        {"D": "Competitivo", "I": "Animado", "S": "Apoiador", "C": "Cuidadoso"},
        # Bloco 5
        {"D": "Destemido", "I": "Influente", "S": "Tranquilo", "C": "Disciplinado"},
        # Bloco 6
        {"D": "Direto", "I": "Otimista", "S": "Cooperativo", "C": "Detalhista"},
        # Bloco 7
        {"D": "Firme", "I": "Expressivo", "S": "Leal", "C": "Sistemático"},
        # Bloco 8
        {"D": "Ousado", "I": "Comunicativo", "S": "Gentil", "C": "Perfeccionista"},
        # Bloco 9
        {"D": "Dominante", "I": "Magnético", "S": "Pacífico", "C": "Lógico"},
        # Bloco 10
        {"D": "Autoritário", "I": "Amigável", "S": "Tolerante", "C": "Criterioso"},
        # Bloco 11
        {"D": "Energético", "I": "Popular", "S": "Moderado", "C": "Racional"},
        # Bloco 12
        {"D": "Exigente", "I": "Alegre", "S": "Acolhedor", "C": "Organizado"},
        # Bloco 13
        {"D": "Independente", "I": "Estimulante", "S": "Confiável", "C": "Prudente"},
        # Bloco 14
        {"D": "Determinado", "I": "Convincente", "S": "Harmonioso", "C": "Diplomata"},
        # Bloco 15
        {"D": "Confiante", "I": "Extrovertido", "S": "Condescendente", "C": "Objetivo"},
        # Bloco 16
        {"D": "Resoluto", "I": "Charmoso", "S": "Amável", "C": "Planejador"},
        # Bloco 17
        {"D": "Comandante", "I": "Inspirador", "S": "Flexível", "C": "Rigoroso"},
        # Bloco 18
        {"D": "Autônomo", "I": "Brincalhão", "S": "Prestativo", "C": "Reservado"},
        # Bloco 19
        {"D": "Persistente", "I": "Envolvente", "S": "Silencioso", "C": "Formal"},
        # Bloco 20
        {"D": "Focado", "I": "Caloroso", "S": "Estacionário", "C": "Discreto"},
        # Bloco 21
        {"D": "Corajoso", "I": "Falante", "S": "Compreensivo", "C": "Justo"},
        # Bloco 22
        {"D": "Rápido", "I": "Expansivo", "S": "Afetuoso", "C": "Estruturado"},
        # Bloco 23
        {"D": "Ambicioso", "I": "Convincente", "S": "Estável", "C": "Metódico"},
        # Bloco 24
        {"D": "Impaciente", "I": "Sociável", "S": "Calmo", "C": "Preciso"}
    ]

    item_id_counter = 100
    if should_seed_base_items:
        for idx, block in enumerate(disc_blocks):
            block_num = idx + 1
            for dim, word in block.items():
                item_id_counter += 1
                item = QuestionnaireItem(
                    id=item_id_counter,
                    block_number=block_num,
                    test_type="DISC",
                    dimension=dim,
                    item_text=word,
                    weight=1.0
                )
                db.add(item)
        print("Seed do DISC finalizado (96 adjetivos).")

    # 6. Seed de Itens de Spranger (24 Afirmações, Likert 1-6)
    spranger_items = [
        # Teorico
        {"dim": "teorico", "text": "Busco entender a lógica científica por trás do funcionamento das coisas."},
        {"dim": "teorico", "text": "Gosto de ler, estudar e aprender constantemente sobre novos conceitos e teorias."},
        {"dim": "teorico", "text": "A busca pela verdade e pelo conhecimento sistemático é o meu maior motivador."},
        {"dim": "teorico", "text": "Prefiro analisar dados numéricos e fatos comprovados antes de formular opiniões."},
        # Economico
        {"dim": "economico", "text": "Maximizar o retorno financeiro ou financeiramente viável é minha prioridade em projetos."},
        {"dim": "economico", "text": "Foco em resultados práticos, utilidade prática e economia no uso de recursos."},
        {"dim": "economico", "text": "Avalio o sucesso das coisas ou de uma carreira pelo seu valor financeiro ou patrimonial."},
        {"dim": "economico", "text": "Acho perda de tempo e esforço focar em ideias bonitas que não dão retorno prático."},
        # Estetico
        {"dim": "estetico", "text": "A harmonia visual, design e arte são cruciais no meu ambiente pessoal e de trabalho."},
        {"dim": "estetico", "text": "Valorizo a criatividade artística, a expressão individual e a beleza estética."},
        {"dim": "estetico", "text": "Aprecio a forma e a harmonia das coisas acima de sua utilidade estritamente prática."},
        {"dim": "estetico", "text": "Busco ativamente experiências marcantes que inspirem meus sentimentos e sentidos."},
        # Social
        {"dim": "social", "text": "Sinto grande satisfação interna em ajudar outras pessoas sem esperar recompensa ou mérito."},
        {"dim": "social", "text": "O bem-estar e a felicidade do grupo são mais importantes que meu próprio sucesso individual."},
        {"dim": "social", "text": "Dedico meu tempo pessoal de forma espontânea para apoiar e aconselhar pessoas necessitadas."},
        {"dim": "social", "text": "Minhas decisões diárias são guiadas majoritariamente por empatia, compaixão e amor humano."},
        # Individualista
        {"dim": "individualista", "text": "Gosto de assumir papéis de liderança direta e influenciar os rumos de projetos grandes."},
        {"dim": "individualista", "text": "Conquistar reconhecimento social, status e autoridade pessoal me motiva fortemente."},
        {"dim": "individualista", "text": "Prefiro ter total autonomia e controle sobre minhas próprias tarefas e tomadas de decisão."},
        {"dim": "individualista", "text": "A busca por destaque, visibilidade e crescimento rápido de carreira é essencial para mim."},
        # Regulador
        {"dim": "regulador", "text": "Sigo regras claras, princípios éticos e estruturas organizacionais estabelecidas rigorosamente."},
        {"dim": "regulador", "text": "Valorizo muito a tradição, a ordem social estabelecida e o respeito estrito aos regulamentos."},
        {"dim": "regulador", "text": "Acredito que sistemas rígidos e estruturados de vida mantêm o ambiente justo e organizado."},
        {"dim": "regulador", "text": "Prefiro seguir métodos tradicionais validados do que inovações conceituais arriscadas."}
    ]

    if should_seed_base_items:
        for idx, item_data in enumerate(spranger_items):
            item_id_counter += 1
            item = QuestionnaireItem(
                id=item_id_counter,
                block_number=idx + 1,
                test_type="SPRANGER",
                dimension=item_data["dim"],
                item_text=item_data["text"],
                weight=1.0
            )
            db.add(item)
        print("Seed do Spranger finalizado (24 afirmações).")

    # 7. Seed de Itens de Jung (24 Afirmações, Likert 1-6)
    jung_items = [
        # E vs I
        {"dim": "E", "text": "Ganho energia física e mental interagindo ativamente com grandes grupos de pessoas."},
        {"dim": "I", "text": "Prefiro refletir silenciosamente sozinho antes de externar uma opinião ou tomar uma decisão."},
        {"dim": "I", "text": "Sinto-me mentalmente exausto após passar muito tempo em reuniões cheias ou eventos sociais."},
        {"dim": "E", "text": "Costumo iniciar conversas facilmente e manter contato mesmo com pessoas que acabei de conhecer."},
        {"dim": "E", "text": "Prefiro resolver problemas conversando abertamente com outros do que pensando isolado."},
        {"dim": "I", "text": "Valorizo muito meu espaço privado e reservo momentos diários de introspecção intocáveis."},
        # S vs N
        {"dim": "S", "text": "Foco minha atenção em fatos realistas, dados práticos e detalhes concretos do presente."},
        {"dim": "N", "text": "Gosto de focar em possibilidades futuras, conexões abstratas e conceitos visionários."},
        {"dim": "S", "text": "Sou conhecido por ser uma pessoa prática, pé no chão e focada em resultados realistas."},
        {"dim": "N", "text": "Gosto de imaginar novos cenários, analogias conceituais e ideias totalmente inovadoras."},
        {"dim": "S", "text": "Prefiro seguir instruções detalhadas passo a passo do que atuar sobre diretrizes abstratas."},
        {"dim": "N", "text": "Prefiro focar no 'porquê' e no significado geral das coisas do que me ater a pequenos detalhes."},
        # T vs F
        {"dim": "T", "text": "Tomo minhas decisões baseado quase inteiramente em lógica fria, raciocínio e fatos analíticos."},
        {"dim": "F", "text": "Busco sempre manter a harmonia do grupo e o bem-estar emocional das pessoas sob minhas decisões."},
        {"dim": "T", "text": "Sou mais influenciado pela lógica técnica de um argumento do que pela sua carga emocional."},
        {"dim": "F", "text": "Considero que os sentimentos das pessoas e o impacto humano são os fatores mais importantes em uma decisão."},
        {"dim": "T", "text": "Acredito que a justiça imparcial e direta é mais importante do que a clemência ou a empatia."},
        {"dim": "F", "text": "Tenho grande facilidade para me colocar no lugar das outras pessoas e compreender suas dores corporativas."},
        # J vs P
        {"dim": "J", "text": "Gosto de manter minha rotina e agenda rigidamente organizadas e planejadas com antecedência."},
        {"dim": "P", "text": "Prefiro manter minhas opções em aberto e me adaptar com flexibilidade aos acontecimentos diários."},
        {"dim": "J", "text": "Finalizar tarefas antes ou exatamente no prazo planejado é uma prioridade na minha vida."},
        {"dim": "P", "text": "Sinto-me extremamente confortável em improvisar e resolver problemas sob pressão de última hora."},
        {"dim": "J", "text": "Aprecio regras de conduta transparentes e processos de trabalho muito bem estabelecidos."},
        {"dim": "P", "text": "Sinto que a rigidez exagerada de cronogramas e planos sufoca minha criatividade e adaptabilidade."}
    ]

    if should_seed_base_items:
        for idx, item_data in enumerate(jung_items):
            item_id_counter += 1
            item = QuestionnaireItem(
                id=item_id_counter,
                block_number=idx + 1,
                test_type="JUNG",
                dimension=item_data["dim"],
                item_text=item_data["text"],
                weight=1.0
            )
            db.add(item)
        print("Seed de Jung finalizado (24 afirmações).")

    # 8. Seed de Itens Big Five (IPIP-50 + atenção, Likert 1-5)
    bigfive_exists = db.query(QuestionnaireItem).filter(
        QuestionnaireItem.test_type == "BIGFIVE"
    ).first()
    if bigfive_exists:
        print("Itens Big Five já cadastrados. Pulando seed do Big Five.")
    else:
        for item_data in construir_itens_bigfive():
            item = QuestionnaireItem(
                id=item_data["id"],
                block_number=item_data["block_number"],
                test_type=item_data["test_type"],
                dimension=item_data["dimension"],
                item_text=item_data["item_text"],
                weight=item_data["weight"],
                reverse_keyed=item_data["reverse_keyed"]
            )
            db.add(item)
        print("Seed do Big Five finalizado (50 itens IPIP + 3 itens de atenção).")

    db.commit()
    print("Banco de dados populado com sucesso!")

if __name__ == "__main__":
    db = SessionLocal()
    try:
        seed_db(db)
    finally:
        db.close()
