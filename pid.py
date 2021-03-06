import numpy as np
import matplotlib
from matplotlib import pyplot

class PID:
	"""
	Discrete PID control
	"""

	def __init__(self, P=2.0, I=0.0, D=1.0, Derivator=0, Integrator=0, Integrator_max=500, Integrator_min=-500):

		self.Kp=P
		self.Ki=I
		self.Kd=D
		self.Derivator=Derivator
		self.Integrator=Integrator
		self.Integrator_max=Integrator_max
		self.Integrator_min=Integrator_min

		self.set_point=0.0
		self.error=5.0

	def update(self,current_value):
		"""
		Calculate PID output value for given reference input and feedback
		"""

		self.error = self.set_point - current_value
		#print(self.Derivator,",",self.Kp,",",self.Ki,",",self.Kd)
		self.P_value = self.Kp * self.error
		self.D_value = self.Kd * ( self.error - self.Derivator)
		self.Derivator = self.error

		self.Integrator = self.Integrator + self.error

		if self.Integrator > self.Integrator_max:
			self.Integrator = self.Integrator_max
		elif self.Integrator < self.Integrator_min:
			self.Integrator = self.Integrator_min

		self.I_value = self.Integrator * self.Ki

		PID = self.P_value + self.I_value + self.D_value

		return PID

	def setPoint(self,set_point):
		"""
		Initilize the setpoint of PID
		"""
		self.set_point = set_point
		self.Integrator=0
		self.Derivator=0

	def setIntegrator(self, Integrator):
		self.Integrator = Integrator

	def setDerivator(self, Derivator):
		self.Derivator = Derivator

	def setKp(self,P):
		self.Kp=P

	def setKi(self,I):
		self.Ki=I

	def setKd(self,D):
		self.Kd=D

	def getPoint(self):
		return self.set_point

	def getError(self):
		return self.error

	def getIntegrator(self):
		return self.Integrator

	def getDerivator(self):
		return self.Derivator


p=PID(0.833,0,1)
p.setPoint(120)
p.setDerivator(119)
if x>15:
        k=p.update(x)
        #pwm left=100-k right=100
elif x<-15:
        x=x*(-1)
        k=p.update(x)
        #pwm left=100 right=100-k

elif x<15 and x>-15:
        k=0
else
        #pwm left=0 righ=0
#x2=[]
#for x in range(1,240,1):
#        print (x)
#        k.append(p.update(x))
#        print(p.set_point)
#        x2.append(x)
#        print(x,',',k)
#print(x2)
#print(k)
#myplot=np.ones([len(k),len(x2)],np.float)*255
#for i in range(0,len(k)-1):
#        myplot[i,x2[i]]=k[i]


#pyplot.plot(k)
#pyplot.show()
#p.update(2.75)

#print(p.P_value)






#while True:
#     pid = p.update(measurement_value)
#
#
