# MODULE: TypeRig / Core / Atom (Objects)
# NOTE: Assorted atomic, generic objects
# -----------------------------------------------------------
# (C) Vassil Kateliev, 2020 		(http://www.kateliev.com)
# (C) Karandash Type Foundry 		(http://www.karandash.eu)
#------------------------------------------------------------
# www.typerig.com

# No warranties. By using this you agree
# that you use it at your own risk!

__version__ = '0.0.2'

# - Dependencies ------------------------
#import collections.abc

# - Objects ----------------------------
class Member(object):
	''' Node primitive that is a member of a sequence. '''
	def __init__(self, data, **kwargs):
		self.data = data
		self.parent = kwargs.get('parent', None)

	def __repr__(self):
		return self.data

	# - Properties -----------------------
	@property
	def next(self):
		try:
			return self.parent[self.parent.index(self) + 1]
		except (IndexError, AttributeError) as error:
			return None
	
	@property
	def prev(self):
		try:
			return self.parent[self.parent.index(self) - 1]
		except (IndexError, AttributeError) as error:
			return None

class Linker(object):
	''' Doubly-linked-list/node primitive. '''
	def __init__(self, data, **kwargs):
		self.data = data
		self.parent = kwargs.get('parent', None)
		self.next = kwargs.get('next', None)
		self.prev = kwargs.get('prev', None)
		self.start = kwargs.get('start', False)

	def __add__(self, other):
		if isinstance(other, self.__class__):
			if isinstance(self.next, self.__class__):
				temp_link = self.next
				temp_link.prev = other
				other.next = temp_link
				self.next = other

			elif self.next is None:
				self.next = other

			return self

	def __sub__(self, other):
		if isinstance(other, self.__class__) and self.next == other:
			temp_link = self.next.next
			temp_link.prev = self
			self.next = temp_link

			return self

	def __iter__(self):
		curr_link = self

		while curr_link is not None: # and not curr_link.next.start:
			yield curr_link
			
			curr_link = curr_link.next

	def __repr__(self):
		return str(self.data)

	# - Functions ------------------
	def where(self, search, value):
		curr_link = self

		while curr_link is not None:
			if eval('curr_link.{}{}'.format(search, value)):
				yield curr_link
			
			curr_link = curr_link.next

		