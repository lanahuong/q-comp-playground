import qiskit as qk
import qiskit.tools.visualization as visu
from qiskit.tools.visualization import plot_state_city
import matplotlib.pyplot as plt
import math

def build_increment_op(n, circ=False):
    inc_op_circ = qk.QuantumCircuit(qk.QuantumRegister(n, "x"))
    for i in range(n-1, 0, -1):
        inc_op_circ.mcx([*range(i)], i, None, "noancilla")
    inc_op_circ.x(0)
    if circ:
        return inc_op_circ
    return inc_op_circ.to_gate(label="S++").control(1)

def build_decrement_op(n, circ=False):
    dec_op_circ = qk.QuantumCircuit(qk.QuantumRegister(n, "x"))
    dec_op_circ.x(0)
    for i in range(1, n):
        dec_op_circ.mcx([*range(i)], i, None, "noancilla")
    if circ:
        return dec_op_circ
    return dec_op_circ.to_gate(label="S--").control(1)

def build_step_cicuit(n):
    # circuit with 1 control qbit and n position qubits and n measure classical bits
    cb = qk.QuantumRegister(1, "c")
    xb = qk.QuantumRegister(n, "x")
    step_circuit = qk.QuantumCircuit(cb, xb, name="Q-step")

    # Get operators
    inc_op = build_increment_op(n)
    dec_op = build_decrement_op(n)

    # build one iteration of the walk
    step_circuit.h(0)
    step_circuit.append(inc_op, [*range(n+1)])
    step_circuit.x(0)
    step_circuit.append(dec_op, [*range(n+1)])
    step_circuit.x(0)

    return step_circuit

def build_walk_cicuit(n, t):
    step_circuit = build_step_cicuit(n)

    cb = qk.QuantumRegister(1, "c")
    xb = qk.QuantumRegister(n, "x")
    mb = qk.ClassicalRegister(n, "m")
    walk_circuit = qk.QuantumCircuit(cb, xb, mb)
    walk_circuit.x(n)
    walk_circuit = walk_circuit.compose(step_circuit.repeat(t))
    for i in range(n):
        walk_circuit.measure(qubit=i+1, cbit=i)
    return walk_circuit

t = 50
n = math.ceil(math.log(t)/math.log(2)+2)
walk_circuit = build_walk_cicuit(n,t)
simulator = qk.Aer.get_backend("aer_simulator")
circ = qk.transpile(walk_circuit, simulator)
result = simulator.run(circ).result()

counts = result.get_counts(circ)
hist = visu.plot_distribution(counts, figsize=(7, 6), title=f'Hadamard Walk after {t} steps sur Z/2^{n}Z', filename="hist.png")
plt.clf()
"hist.png"
