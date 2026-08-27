=== Scenario 1: normal refund (should be allowed) ===

[Complete Response] -> Message(id='msg_011CeSQLhcU61hT5dbhC5pFm', container=None, content=[TextBlock(citations=None, text="I'll verify your identity and process the refund for you.", type='text'), ToolUseBlock(id='toolu_01UB5VNvRwZX7fLTR7muWGxM', caller=DirectCaller(type='direct'), input={'email': 'ali@example.com'}, name='get_customer', type='tool_use', toolset_name=None)], model='claude-haiku-4-5-20251001', role='assistant', stop_details=None, stop_reason='tool_use', stop_sequence=None, type='message', usage=Usage(cache_creation=CacheCreation(ephemeral_1h_input_tokens=0, ephemeral_5m_input_tokens=0), cache_creation_input_tokens=0, cache_read_input_tokens=0, inference_geo='not_available', input_tokens=690, output_tokens=71, output_tokens_details=None, server_tool_use=None, service_tier='standard'))

[stop_reason] -> tool_use
[tool_use] name=get_customer, input={'email': 'ali@example.com'}
[tool_result] -> {'customer_id': 'CUST-1001', 'name': 'Ali Raza', 'last_purchase_date': '2024-06-27'}

[Complete Response] -> Message(id='msg_011CeSQLn3crMCP5iWgWya3j', container=None, content=[TextBlock(citations=None, text="Great! Now I'll process your $200 refund.", type='text'), ToolUseBlock(id='toolu_018Q4J3wxbgTkRDNXLTLFXjr', caller=DirectCaller(type='direct'), input={'customer_id': 'CUST-1001', 'amount': 200}, name='process_refund', type='tool_use', toolset_name=None)], model='claude-haiku-4-5-20251001', role='assistant', stop_details=None, stop_reason='tool_use', stop_sequence=None, type='message', usage=Usage(cache_creation=CacheCreation(ephemeral_1h_input_tokens=0, ephemeral_5m_input_tokens=0), cache_creation_input_tokens=0, cache_read_input_tokens=0, inference_geo='not_available', input_tokens=810, output_tokens=92, output_tokens_details=None, server_tool_use=None, service_tier='standard'))

[stop_reason] -> tool_use
[tool_use] name=process_refund, input={'customer_id': 'CUST-1001', 'amount': 200}
[tool_result] -> {'status': 'success', 'customer_id': 'CUST-1001', 'refunded_amount': 200}

[Complete Response] -> Message(id='msg_011CeSQLrnNoCYc4TZB1wANC', container=None, content=[TextBlock(citations=None, text='Perfect! Your $200 refund has been successfully processed. You should see it reflected in your account shortly. Is there anything else I can help you with?', type='text')], model='claude-haiku-4-5-20251001', role='assistant', stop_details=None, stop_reason='end_turn', stop_sequence=None, type='message', usage=Usage(cache_creation=CacheCreation(ephemeral_1h_input_tokens=0, ephemeral_5m_input_tokens=0), cache_creation_input_tokens=0, cache_read_input_tokens=0, inference_geo='not_available', input_tokens=941, output_tokens=36, output_tokens_details=None, server_tool_use=None, service_tier='standard'))

[stop_reason] -> end_turn

Agent's final reply: Perfect! Your $200 refund has been successfully processed. You should see it reflected in your account shortly. Is there anything else I can help you with?

=== Scenario 2: refund above threshold (should be blocked) ===

[Complete Response] -> Message(id='msg_011CeSQLvkVq2StXaEvroMp5', container=None, content=[ToolUseBlock(id='toolu_0112STBrkEmQVS16xRcz4UyQ', caller=DirectCaller(type='direct'), input={'email': 'sara@example.com'}, name='get_customer', type='tool_use', toolset_name=None)], model='claude-haiku-4-5-20251001', role='assistant', stop_details=None, stop_reason='tool_use', stop_sequence=None, type='message', usage=Usage(cache_creation=CacheCreation(ephemeral_1h_input_tokens=0, ephemeral_5m_input_tokens=0), cache_creation_input_tokens=0, cache_read_input_tokens=0, inference_geo='not_available', input_tokens=690, output_tokens=58, output_tokens_details=None, server_tool_use=None, service_tier='standard'))

[stop_reason] -> tool_use
[tool_use] name=get_customer, input={'email': 'sara@example.com'}
[tool_result] -> {'customer_id': 'CUST-2002', 'name': 'Sara Khan', 'last_purchase_date': '2024-07-26'}

[Complete Response] -> Message(id='msg_011CeSQLzbg4qVY4HZs7JPs5', container=None, content=[TextBlock(citations=None, text="Great! I've verified your account. Now processing 
your $800 refund.", type='text'), ToolUseBlock(id='toolu_01WYsSGs5irkqaX8dfSz1smX', caller=DirectCaller(type='direct'), input={'customer_id': 'CUST-2002', 'amount': 800}, name='process_refund', type='tool_use', toolset_name=None)], model='claude-haiku-4-5-20251001', role='assistant', stop_details=None, stop_reason='tool_use', stop_sequence=None, type='message', usage=Usage(cache_creation=CacheCreation(ephemeral_1h_input_tokens=0, ephemeral_5m_input_tokens=0), cache_creation_input_tokens=0, cache_read_input_tokens=0, inference_geo='not_available', input_tokens=795, output_tokens=96, output_tokens_details=None, server_tool_use=None, service_tier='standard'))

[stop_reason] -> tool_use
[tool_use] name=process_refund, input={'customer_id': 'CUST-2002', 'amount': 800}
[PreToolUse hook] BLOCKED: amount exceeds auto-approval threshold of $500 (PreToolUse hook).

[HANDOFF SUMMARY - escalated to human agent]
  customer_id: CUST-2002
  requested_amount: $800
  root_cause: BLOCKED: amount exceeds auto-approval threshold of $500 (PreToolUse hook).
  recommended_action: Manual review required before refund can be approved.

[tool_result] -> {'status': 'blocked', 'reason': 'BLOCKED: amount exceeds auto-approval threshold of $500 (PreToolUse hook).', 'escalated_to_human': True}

[Complete Response] -> Message(id='msg_011CeSQM6RAQ9iMN7KACi1KU', container=None, content=[TextBlock(citations=None, text="Your refund request for $800 has been flagged as it exceeds our auto-approval threshold of $500. The case has been escalated to our team for manual review. We'll follow up with you shortly. Is there anything else I can help with?", type='text')], model='claude-haiku-4-5-20251001', role='assistant', stop_details=None, stop_reason='end_turn', stop_sequence=None, type='message', usage=Usage(cache_creation=CacheCreation(ephemeral_1h_input_tokens=0, ephemeral_5m_input_tokens=0), cache_creation_input_tokens=0, cache_read_input_tokens=0, inference_geo='not_available', input_tokens=944, output_tokens=58, output_tokens_details=None, server_tool_use=None, service_tier='standard'))

[stop_reason] -> end_turn

Agent's final reply: Your refund request for $800 has been flagged as it exceeds our auto-approval threshold of $500. The case has been escalated to our team for manual review. We'll follow up with you shortly. Is there anything else I can help with?

=== Task 1.7 demo: save & resume a session (no extra API call) ===

[Session saved] -> session_state.json
[Session loaded] -> session_state.json (6 messages restored, no new API call needed)