# pyboids
A boids flocking behaviour algorithm implementation in Python and Pygame


## The basics

### How it all works

This is a simulation that aims at representing or recreating the behaviour of flocking birds. There are three rules that the boids simulation relies on :

- alignment : the velocities of nearby boids tend to align.
- cohesion : boids like to be together, but...
- separation : boids tend to repel when they are too near from one another.

Here is how we can implement these rules in the simulation :

- alignment : assign velocity of boids `b` the average velocity of "nearby" (we'll have to define this term) boids
- cohesion : average the position of nearby boids and move a bit towards that position
- separation : if a stranger boid enters a critical radius, move away from it with a velocity directed in the opposite direction.

Each of these will in practice be associated with a modification of the velocity at next time step.

### Rules in equation

**Notations.** Given a set of $N$ boids and a time of simulation $t^n$ :

- let $v^n_i$ and $p^n_i$ respectively be the velocity and position of a boid of interest $i$ ;
- let $v^n_i$ and $p^n_j$ respectively be the velocity and position of any other boid $j$, $j \neq i$ ;
- let $m_i$ be the number of boids in the neighborhood of current boid $i$, the latter being excluded.

#### Alignment

Alignment translates to a contribution $v_a$ to the next velocity $v^{n+1}_i$ given be the center of mass of neighbors' velocities :

$$ v_a = K_a ((\frac{1}{m_i}\sum_{j=1}^{m_i} v^n_j) - v^n_i) $$

where $K_a$ is typically around 0.1 or 0.15.

#### Cohesion

Cohesion means that boids tend to fly together (that is, to fly towards the center of mass of their neighbors' positions), hence a contribution $v_c$ to the next velocity $v^{n+1}_i$ given by :

$$ v_c = K_c ((\frac{1}{m_i} \sum_{j=1}^{m_i} p^n_j) - p^n_i)$$

where $K_c$ is typically around 0.01.

#### Separation

Separation refers to the fact that near boids tend to repel one another, as they don't like that much to be too close. This yields to a contribution $v_s$ given by :

$$ v_s = - \sum_{j,\ dist(i, j)\ \leq\ R_s} (p_j^n - v^n_i) $$

where $R_s$ is the critical radius of separation. Only boids $j$ closer than $R_s$ contribute to the separation effect. The overall "density" of the flocking will then be given by this parameter.

#### Bounding the velocity

In reality, birds can't go arbitrarily fast. We can add another rule to limit the velocity of boids with a $v_{lim}$ parameter. Typical value could be 20.

#### Bounding the position

For simulation purposes, boids will need to remain in a given box (the screen). We will simply say that if the position in $x$ or $y$ direction exceeds a certain amount, then add a velocity $v_b$ in the opposite direction to induce a smooth return to the simulation space. Typical value of $v_b$ is around 10.

#### Noise addition

To create a more realistic feel, we can add multiplicative noise to the new velocity $v^{n+1}_i$ with a factor $(1 + \eta_{n+1})$ where $\eta$ is a given random distribution, typically $\mathcal{N}(0, 0.2)$.


## Implementation in Python and Pygame

We'll make use of the OOP paradigm to build this simulation.

### Parameters definition

All parameters of the simulation will be grouped in a `params.py` file.

### Class definition

Here are the classes we'll need :

- `Boid` : contains the position and velocity of a given boid and packs several methods implementing the previous rules :
	- `align(self, others)`
	- `cohere(self, others)`
	- `separate(self, others)`
	- `limit_speed(self)`
	- `limit_position(self)`
- `Flock` : groups a certain number of `Boid` objects and manages their interactions.
- `Simulation` : runs the simulation (Pygame application), with interactive functionalities such as :
	- Add a `Boid` by clicking on the screen
	- Turning on/off any the previous rules with the keyboard
	- Start/pause/reset the simulation
	- Display/hide commands or help

## Ressources

http://www.vergenet.net/~conrad/boids/pseudocode.html