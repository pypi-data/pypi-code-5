import gossip

step_hook_group = gossip.create_group("step")
step_hook_group.set_strict()

step_start = gossip.define('step.start')
step_success = gossip.define('step.success')
step_error = gossip.define('step.error')
step_end = gossip.define('step.end')
