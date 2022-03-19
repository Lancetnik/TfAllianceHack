from aiogram.dispatcher.filters.state import StatesGroup as Sg, State as S

from config.dependencies import dp


class State(S):
    async def set(self, *, context=None, history=True):
        if context is None:
            context = dp.get_current().current_state()

        if history is True:
            prev_states = (await context.get_data()).get('prev_state', [])
            last_state = await context.get_state()
            if not prev_states or prev_states[-1] != last_state:
                prev_states.append(last_state)
                await context.update_data({
                    'prev_state': prev_states
                })

        await context.set_state(self.state)
        return context

    def __eq__(self, o):
        return self.state == o.state


class StatesGroup(Sg):
    @classmethod
    async def next(cls) -> str:
        state = dp.get_current().current_state()
        state_name = await state.get_state()

        try:
            next_step = cls.states_names.index(state_name) + 1
        except ValueError:
            next_step = 0

        try:
            next_state = cls.states[next_step]
        except IndexError:
            await state.set_state(None)
            return None

        await next_state.set()
        return next_state.state

    @classmethod
    async def previous(cls) -> str:
        state = dp.get_current().current_state()
        state_name = await state.get_state()

        try:
            if history := (await state.get_data()).get('prev_state'):
                previous_step = cls.states_names.index(history[-1])
                await state.update_data({'prev_state': history[:-1]})
            else:
                previous_step = cls.states_names.index(state_name) - 1
        except ValueError:
            previous_step = 0

        if previous_step < 0:
            await state.set_state(None)
            return None
        else:
            previous_state = cls.states[previous_step]

        await previous_state.set(history=False)
        return previous_state.state

    @classmethod
    async def first(cls) -> str:
        first_state = cls.states[0]
        await first_state.set()
        return first_state.state

    @classmethod
    async def last(cls) -> str:
        last_state = cls.states[-1]
        await last_state.set()
        return last_state.state
