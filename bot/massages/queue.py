async def create_massage(rows, info, key):
    if not rows: return {"mes": "📭 Очередь пуста","func": key.not_list}
        
    messages = []
    for i, r in enumerate(rows, 1):
        user_info = await info.get_user_info(r['user_id'])
        name = user_info.get('firstname')
        surname = user_info.get('surname')
        username = user_info.get('username')
        status = "✅" if r['is_pass'] else "⏳"
        messages.append(f"{i}. {status} {name} {surname} @{username}")

    return {"mes" :"📋 Очередь:\n" + "\n".join(messages), "func": key.is_list}